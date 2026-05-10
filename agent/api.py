"""FastAPI app — punto de entrada del agente.

Run:
    uvicorn agent.api:app --reload --port 8000
"""
import asyncio
import os
import random
from contextlib import asynccontextmanager
from datetime import datetime, timezone

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# cargar .env del directorio padre
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from agent.state import state
from agent.policy import DEFAULT_POLICY
from agent.detector import Detector
from agent.notifier import Notifier
from agent.ai_filter import AIFilter
from agent.escalation import EscalationAgent
from agent.models import AnomalyEvent, EventType, Vitals


# === Wiring de dependencias ===
USE_MOCK_SOLANA = os.getenv("USE_MOCK_SOLANA", "true").lower() == "true"
USE_MQTT = os.getenv("USE_MQTT", "false").lower() == "true"

if USE_MOCK_SOLANA:
    from agent.solana_writer_mock import MockSolanaWriter
    solana_writer = MockSolanaWriter()
    print("[API] usando MockSolanaWriter (USE_MOCK_SOLANA=true)")
else:
    from agent.solana_writer import SolanaWriter  # noqa: F401
    solana_writer = SolanaWriter()
    print("[API] usando SolanaWriter real")

notifier = Notifier()
ai_filter = AIFilter()
detector = Detector(DEFAULT_POLICY)
escalation = EscalationAgent(DEFAULT_POLICY, notifier, solana_writer, ai_filter)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if USE_MQTT:
        from agent.subscriber import subscribe_loop
        task = asyncio.create_task(subscribe_loop(detector, escalation))
        print("[API] MQTT subscriber iniciado")
    else:
        task = None
        print("[API] MQTT deshabilitado (USE_MQTT=false) — usar POST /api/simulate")
    try:
        yield
    finally:
        if task:
            task.cancel()
            print("[API] MQTT subscriber detenido")


app = FastAPI(title="TE CUIDO Agent", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Helpers de serialización ===

def _serialize_vitals(v):
    if v is None:
        return None
    return {
        "heart_rate": round(v.heart_rate, 1),
        "spo2": round(v.spo2, 1),
        "skin_temp": round(v.skin_temp, 1),
        "is_moving": v.is_moving,
        "timestamp": v.timestamp,
    }


def _serialize_event(e):
    if e is None:
        return None
    return {
        "id": e.id,
        "type": e.type.value,
        "severity": e.severity,
        "value": e.value,
        "timestamp": e.timestamp,
        "event_started_at": e.event_started_at,
        "resolved": e.resolved,
        "resolved_at": e.resolved_at,
        "actions": [
            {
                "type": a.type.value,
                "timestamp": a.timestamp,
                "tx_hash": a.tx_hash,
                "contact_index": a.contact_index,
                "note": a.note,
            }
            for a in e.actions
        ],
    }


# === Endpoints ===

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/status")
def status():
    grace_remaining = None
    if (
        state.status == "alert"
        and state.active_event
        and state.active_event.event_started_at
    ):
        started = datetime.fromisoformat(state.active_event.event_started_at)
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        grace_remaining = max(0, int(DEFAULT_POLICY.grace_period_secs - elapsed))

    return {
        "status": state.status,
        "patient": {
            "name": os.getenv("PATIENT_NAME", "Carmen García"),
            "age": int(os.getenv("PATIENT_AGE", "78")),
        },
        "vitals": _serialize_vitals(state.last_vitals),
        "active_event": _serialize_event(state.active_event),
        "history": [_serialize_event(e) for e in state.history[:10]],
        "grace_seconds_remaining": grace_remaining,
    }


@app.post("/api/wellbeing")
def wellbeing():
    """El familiar (o Carmen desde el dispositivo) confirma que está bien."""
    state.wellbeing_confirmed = True
    return {"ok": True}


# === Demo / Simulación ===

def _make_vitals_for(event_type: str) -> tuple[Vitals, AnomalyEvent]:
    """Genera vitals sintéticas + AnomalyEvent para el tipo de evento pedido."""
    now_iso = datetime.now(timezone.utc).isoformat()

    if event_type == "fall":
        vitals = Vitals(
            heart_rate=round(random.uniform(68, 80), 1),
            spo2=round(random.uniform(95, 99), 1),
            skin_temp=round(random.uniform(36.2, 36.8), 1),
            accel_x=round(random.uniform(-1.5, 1.5), 2),
            accel_y=round(random.uniform(-1.5, 1.5), 2),
            accel_z=round(random.uniform(3.5, 4.5), 2),  # spike de impacto
            gyro_x=0.0, gyro_y=0.0, gyro_z=0.0,
            is_moving=False,
            timestamp=now_iso,
        )
        event = AnomalyEvent(
            type=EventType.FALL,
            severity=3,
            value=round((vitals.accel_x**2 + vitals.accel_y**2 + vitals.accel_z**2) ** 0.5, 2),
            timestamp=now_iso,
        )

    elif event_type == "low_spo2":
        spo2_val = round(random.uniform(84, 89), 1)
        vitals = Vitals(
            heart_rate=round(random.uniform(68, 78), 1),
            spo2=spo2_val,
            skin_temp=round(random.uniform(36.0, 36.5), 1),
            accel_x=0.0, accel_y=0.0, accel_z=1.0,
            gyro_x=0.0, gyro_y=0.0, gyro_z=0.0,
            is_moving=True,
            timestamp=now_iso,
        )
        event = AnomalyEvent(
            type=EventType.LOW_SPO2,
            severity=2,
            value=spo2_val,
            timestamp=now_iso,
        )

    else:  # low_hr (default)
        hr_val = round(random.uniform(34, 41), 1)
        vitals = Vitals(
            heart_rate=hr_val,
            spo2=round(random.uniform(93, 97), 1),
            skin_temp=round(random.uniform(36.2, 36.6), 1),
            accel_x=0.0, accel_y=0.0, accel_z=1.0,
            gyro_x=0.0, gyro_y=0.0, gyro_z=0.0,
            is_moving=True,
            timestamp=now_iso,
        )
        event = AnomalyEvent(
            type=EventType.LOW_HR,
            severity=2,
            value=hr_val,
            timestamp=now_iso,
        )

    return vitals, event


@app.post("/api/simulate")
async def simulate(event_type: str = "low_hr"):
    """
    Inyecta un evento simulado sin necesitar MQTT.

    event_type: "low_hr" | "low_spo2" | "fall"

    Ejemplo:
        curl -X POST "http://localhost:8000/api/simulate?event_type=fall"
    """
    event_type = event_type.lower()
    if event_type not in ("low_hr", "low_spo2", "fall"):
        raise HTTPException(status_code=400, detail="event_type debe ser: low_hr, low_spo2, fall")

    if escalation._handling:
        raise HTTPException(status_code=409, detail="Ya hay un evento activo — esperá que se resuelva o confirmá bienestar")

    # Poblar recent_vitals con 10 lecturas sintéticas para que Gemini tenga contexto
    for _ in range(10):
        vitals, _ = _make_vitals_for(event_type)
        state.recent_vitals.append(vitals)

    # Lectura final = el evento que dispara la escalada
    vitals, anomaly = _make_vitals_for(event_type)
    state.last_vitals = vitals
    state.recent_vitals.append(vitals)

    asyncio.create_task(escalation.handle(anomaly))

    return {
        "ok": True,
        "event_type": anomaly.type.value,
        "value": anomaly.value,
        "message": "Escalada iniciada — monitoreá /api/status para ver el progreso",
    }
