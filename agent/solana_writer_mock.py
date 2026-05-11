import uuid

from agent.models import AnomalyEvent, ActionType


class MockSolanaWriter:
    """Simulates on-chain writes. Returns fake PDAs and tx hashes.
    Replace with real SolanaWriter (anchorpy) once the contract is deployed on Playground."""

    async def register_event(self, event: AnomalyEvent) -> tuple[str, str]:
        pda = f"mockPDA{uuid.uuid4().hex[:32]}"
        tx = f"mockTx{uuid.uuid4().hex[:38]}"
        print(f"[MOCK SOLANA] register_event {event.type.value} → pda={pda[:16]}... tx={tx[:16]}...")
        return pda, tx

    async def register_action(
        self,
        event_pda: str,
        action_type: ActionType,
        contact_index: int = 0,
        note: str = "",
    ) -> str:
        tx = f"mockTx{uuid.uuid4().hex[:38]}"
        suffix = f" idx={contact_index}" if action_type == ActionType.NOTIFIED_CONTACT else ""
        note_str = f' note="{note[:40]}"' if note else ""
        print(f"[MOCK SOLANA] register_action {action_type.value}{suffix}{note_str} → tx={tx[:16]}...")
        return tx

    async def confirm_wellbeing(self, event_pda: str) -> str:
        tx = f"mockTx{uuid.uuid4().hex[:38]}"
        print(f"[MOCK SOLANA] confirm_wellbeing {event_pda[:16]}... → tx={tx[:16]}...")
        return tx
