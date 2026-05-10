import asyncio
from datetime import datetime, timezone

from agent.models import AnomalyEvent, EventLog, AgentAction, ActionType
from agent.policy import EscalationPolicy
from agent.state import state
from agent.notifier import Notifier
from agent.ai_filter import AIFilter


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EscalationAgent:
    """Orquesta los 4 pasos de la escalada:
       0. Evalúa con AI filter (descarta falso positivo)
       1. Ventana de gracia (60s)
       2. Notifica contacto 0
       3. Notifica contacto 1
       4. Escala a emergencia
    Cada paso queda registrado on-chain via solana_writer."""

    def __init__(
        self,
        policy: EscalationPolicy,
        notifier: Notifier,
        solana_writer,
        ai_filter: AIFilter,
    ):
        self.policy = policy
        self.notifier = notifier
        self.solana = solana_writer
        self.ai = ai_filter
        self._handling = False

    async def handle(self, event: AnomalyEvent):
        if self._handling:
            return  # ya hay una escalada activa
        self._handling = True
        try:
            await self._handle_inner(event)
        except Exception as e:
            print(f"[Escalation] error: {e}")
        finally:
            self._handling = False

    async def _handle_inner(self, event: AnomalyEvent):
        # Paso -1: AI filter
        decision = await self.ai.evaluate(event, list(state.recent_vitals))
        razonamiento = decision.get("razonamiento", "")
        confianza = decision.get("confianza", 0.0)
        print(f"[Escalation] AI: real={decision.get('real')} confianza={confianza:.2f} — {razonamiento}")

        # Registrar evento on-chain (siempre, para audit trail)
        event_pda, event_tx = await self.solana.register_event(event)
        event_log = EventLog(
            id=event_pda,
            type=event.type,
            severity=event.severity,
            value=event.value,
            timestamp=event.timestamp,
            event_started_at=_now(),
        )

        if not decision.get("real", True):
            # Caso: AI lo descartó como falso positivo
            tx = await self.solana.register_action(
                event_pda,
                ActionType.AI_DISMISSED,
                note=razonamiento,
            )
            event_log.actions.append(AgentAction(
                type=ActionType.AI_DISMISSED,
                timestamp=_now(),
                tx_hash=tx,
                note=razonamiento,
            ))
            event_log.resolved = True
            event_log.resolved_at = _now()
            state.history.insert(0, event_log)
            state.status = "ok"
            return

        # AI confirmó que es real → arranca escalada
        state.active_event = event_log
        state.status = "alert"
        state.wellbeing_confirmed = False

        # Paso 0: ventana de gracia
        tx = await self.solana.register_action(event_pda, ActionType.GRACE_PERIOD)
        event_log.actions.append(AgentAction(
            type=ActionType.GRACE_PERIOD,
            timestamp=_now(),
            tx_hash=tx,
        ))

        if await self._wait_wellbeing(self.policy.grace_period_secs):
            await self._resolve(event_pda, event_log, "Carmen confirmó que está bien")
            return

        # Paso 1: notificar contacto 0
        state.status = "emergency"
        await self._notify(event, event_pda, event_log, contact_idx=0)
        if await self._wait_wellbeing(self.policy.contact_timeout_secs):
            await self._resolve(event_pda, event_log, "Familiar respondió")
            return

        # Paso 2: notificar contacto 1
        await self._notify(event, event_pda, event_log, contact_idx=1)
        if await self._wait_wellbeing(self.policy.contact_timeout_secs):
            await self._resolve(event_pda, event_log, "Segundo contacto respondió")
            return

        # Paso 3: escalar a emergencia
        await self.notifier.emergency(event)
        tx = await self.solana.register_action(event_pda, ActionType.ESCALATED)
        event_log.actions.append(AgentAction(
            type=ActionType.ESCALATED,
            timestamp=_now(),
            tx_hash=tx,
        ))
        # En este punto el evento queda como activo hasta que alguien manualmente lo resuelva.

    async def _wait_wellbeing(self, timeout: int) -> bool:
        elapsed = 0
        while elapsed < timeout:
            if state.wellbeing_confirmed:
                return True
            await asyncio.sleep(1)
            elapsed += 1
        return False

    async def _notify(self, event, event_pda, event_log, contact_idx: int):
        await self.notifier.send(contact_idx, event)
        tx = await self.solana.register_action(
            event_pda,
            ActionType.NOTIFIED_CONTACT,
            contact_index=contact_idx,
        )
        event_log.actions.append(AgentAction(
            type=ActionType.NOTIFIED_CONTACT,
            timestamp=_now(),
            tx_hash=tx,
            contact_index=contact_idx,
        ))

    async def _resolve(self, event_pda, event_log, note: str):
        tx = await self.solana.confirm_wellbeing(event_pda)
        event_log.actions.append(AgentAction(
            type=ActionType.WELLBEING_CONFIRMED,
            timestamp=_now(),
            tx_hash=tx,
            note=note,
        ))
        event_log.resolved = True
        event_log.resolved_at = _now()
        state.active_event = None
        state.status = "ok"
        state.history.insert(0, event_log)
