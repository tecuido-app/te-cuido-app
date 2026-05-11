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
    """Orchestrates the 4 escalation steps:
       0. AI filter evaluation (dismiss false positive)
       1. Grace period (60s)
       2. Notify contact 0
       3. Notify contact 1
       4. Escalate to emergency
    Every step is logged on-chain via solana_writer."""

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
            return  # escalation already in progress
        self._handling = True
        try:
            await self._handle_inner(event)
        except Exception as e:
            print(f"[Escalation] error: {e}")
        finally:
            self._handling = False

    async def _handle_inner(self, event: AnomalyEvent):
        # Step -1: AI filter
        decision = await self.ai.evaluate(event, list(state.recent_vitals))
        reasoning = decision.get("reasoning", "")
        confidence = decision.get("confidence", 0.0)
        print(f"[Escalation] AI: real={decision.get('real')} confidence={confidence:.2f} — {reasoning}")

        # Register event on-chain (always, for audit trail)
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
            # AI dismissed as false positive
            tx = await self.solana.register_action(
                event_pda,
                ActionType.AI_DISMISSED,
                note=reasoning,
            )
            event_log.actions.append(AgentAction(
                type=ActionType.AI_DISMISSED,
                timestamp=_now(),
                tx_hash=tx,
                note=reasoning,
            ))
            event_log.resolved = True
            event_log.resolved_at = _now()
            state.history.insert(0, event_log)
            state.status = "ok"
            return

        # AI confirmed real event — start escalation
        state.active_event = event_log
        state.status = "alert"
        state.wellbeing_confirmed = False

        # Step 0: grace period
        tx = await self.solana.register_action(event_pda, ActionType.GRACE_PERIOD)
        event_log.actions.append(AgentAction(
            type=ActionType.GRACE_PERIOD,
            timestamp=_now(),
            tx_hash=tx,
        ))

        if await self._wait_wellbeing(self.policy.grace_period_secs):
            await self._resolve(event_pda, event_log, "Patient confirmed wellbeing")
            return

        # Step 1: notify contact 0
        state.status = "emergency"
        await self._notify(event, event_pda, event_log, contact_idx=0)
        if await self._wait_wellbeing(self.policy.contact_timeout_secs):
            await self._resolve(event_pda, event_log, "Contact 1 responded")
            return

        # Step 2: notify contact 1
        await self._notify(event, event_pda, event_log, contact_idx=1)
        if await self._wait_wellbeing(self.policy.contact_timeout_secs):
            await self._resolve(event_pda, event_log, "Contact 2 responded")
            return

        # Step 3: escalate to emergency
        await self.notifier.emergency(event)
        tx = await self.solana.register_action(event_pda, ActionType.ESCALATED)
        event_log.actions.append(AgentAction(
            type=ActionType.ESCALATED,
            timestamp=_now(),
            tx_hash=tx,
        ))
        # Event stays active until manually resolved.

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
