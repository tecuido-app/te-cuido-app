import json
import os

import google.genai as genai
from google.genai import types

from agent.models import Vitals, AnomalyEvent


# Modelo confirmado funcionando con tu API key (gemini-2.0-flash dio 429 cuota 0).
GEMINI_MODEL = "gemini-2.5-flash"


class AIFilter:
    """Pasa el evento candidato + las últimas lecturas a Gemini.
    Devuelve {real, confianza, razonamiento}.
    Si no hay API key, queda deshabilitado y siempre dice real=true."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("[AIFilter] GEMINI_API_KEY o GOOGLE_API_KEY no configurada — filtro deshabilitado")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

    async def evaluate(self, event: AnomalyEvent, recent_vitals: list[Vitals]) -> dict:
        if self.client is None:
            return {
                "real": True,
                "confianza": 1.0,
                "razonamiento": "AI filter deshabilitado (sin API key)",
            }

        readings = "\n".join(
            f"- HR={v.heart_rate:.0f}bpm SpO2={v.spo2:.1f}% "
            f"accel=({v.accel_x:.2f},{v.accel_y:.2f},{v.accel_z:.2f})g "
            f"moving={v.is_moving}"
            for v in recent_vitals[-15:]
        )

        prompt = f"""Sos un asistente médico evaluando una alerta de un sistema de monitoreo de adultos mayores.

PACIENTE: Carmen García, 78 años, vive sola.

EVENTO DETECTADO:
- Tipo: {event.type.value}
- Valor: {event.value:.1f}
- Severidad: {event.severity}/3

ÚLTIMAS LECTURAS (más reciente abajo):
{readings}

¿Es una emergencia real o probablemente un falso positivo (movimiento brusco, sensor mal puesto, sentarse rápido)?

Respondé SOLO un objeto JSON con este formato exacto, sin texto adicional:
{{"real": true|false, "confianza": 0.0-1.0, "razonamiento": "una oración corta en español"}}"""

        try:
            response = await self.client.aio.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[AIFilter] error evaluando, fallback a real=true: {e}")
            return {
                "real": True,
                "confianza": 0.5,
                "razonamiento": f"Fallback (error en IA: {type(e).__name__})",
            }
