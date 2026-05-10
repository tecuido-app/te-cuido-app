"""Real on-chain writer usando anchorpy.

Requiere:
  - PROGRAM_ID en .env (del Playground después del deploy)
  - solana/idl.json descargado del Playground
  - USE_MOCK_SOLANA=false en .env

La wallet se genera automáticamente en .solana-wallet.json y se pide airdrop
en devnet si el balance es bajo.
"""
import asyncio
import json
import os
import time
from pathlib import Path

from anchorpy import Program, Provider, Wallet, Context, Idl
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

from agent.models import AnomalyEvent, ActionType, EventType


WALLET_FILE = Path(__file__).parent.parent / ".solana-wallet.json"
IDL_FILE = Path(__file__).parent.parent / "solana" / "idl.json"

# Mapeos Python → Rust u8 (deben coincidir con los comentarios en lib.rs)
ACTION_TYPE_U8: dict[ActionType, int] = {
    ActionType.GRACE_PERIOD: 0,
    ActionType.AI_DISMISSED: 1,
    ActionType.NOTIFIED_CONTACT: 2,
    ActionType.ESCALATED: 3,
    ActionType.WELLBEING_CONFIRMED: 4,
    ActionType.RESOLVED: 5,
}

EVENT_TYPE_U8: dict[EventType, int] = {
    EventType.FALL: 0,
    EventType.LOW_HR: 1,
    EventType.LOW_SPO2: 2,
}


def _load_or_create_keypair() -> Keypair:
    if WALLET_FILE.exists():
        secret = json.loads(WALLET_FILE.read_text())
        return Keypair.from_bytes(bytes(secret))
    kp = Keypair()
    WALLET_FILE.write_text(json.dumps(list(bytes(kp))))
    print(f"[Solana] Nueva wallet: {kp.pubkey()} — guardada en {WALLET_FILE.name}")
    return kp


class SolanaWriter:
    def __init__(self):
        self._program_id_str = os.getenv("PROGRAM_ID", "").strip()
        self._rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")

        if not self._program_id_str:
            raise ValueError("[Solana] PROGRAM_ID no está en .env — completalo después del Playground deploy")
        if not IDL_FILE.exists():
            raise FileNotFoundError(f"[Solana] IDL no encontrado en {IDL_FILE} — descargalo del Playground")

        self._program_id = Pubkey.from_string(self._program_id_str)
        self._keypair = _load_or_create_keypair()

        with open(IDL_FILE) as f:
            self._idl = Idl.from_json(f.read())

        self._program: Program | None = None
        print(f"[Solana] wallet={self._keypair.pubkey()}")
        print(f"[Solana] program={self._program_id}")
        print(f"[Solana] rpc={self._rpc_url}")

    async def _get_program(self) -> Program:
        if self._program is not None:
            return self._program

        client = AsyncClient(self._rpc_url, commitment=Confirmed)
        wallet = Wallet(self._keypair)
        provider = Provider(client, wallet)

        try:
            resp = await client.get_balance(self._keypair.pubkey())
            if resp.value < 100_000_000:  # < 0.1 SOL
                print("[Solana] balance bajo, pidiendo airdrop en devnet...")
                await client.request_airdrop(self._keypair.pubkey(), 1_000_000_000)
                await asyncio.sleep(3)
        except Exception as e:
            print(f"[Solana] airdrop check falló (ignorando): {e}")

        self._program = Program(self._idl, self._program_id, provider)
        return self._program

    def _derive_pda(self, event_id: int) -> Pubkey:
        pda, _ = Pubkey.find_program_address(
            [b"event", event_id.to_bytes(8, "little")],
            self._program_id,
        )
        return pda

    async def register_event(self, event: AnomalyEvent) -> tuple[str, str]:
        program = await self._get_program()

        event_id = int(time.time() * 1000)  # ms timestamp → event_id único
        event_pda = self._derive_pda(event_id)

        tx = await program.rpc["register_event"](
            event_id,
            EVENT_TYPE_U8.get(event.type, 0),
            event.severity,
            int(event.value * 100),  # i64 fixed-point, 2 decimales
            ctx=Context(
                accounts={
                    "event_log": event_pda,
                    "signer": self._keypair.pubkey(),
                    "system_program": SYS_PROGRAM_ID,
                }
            ),
        )

        pda_str = str(event_pda)
        tx_str = str(tx)
        print(f"[Solana] register_event → pda={pda_str[:16]}... tx={tx_str[:16]}...")
        return pda_str, tx_str

    async def register_action(
        self,
        event_pda: str,
        action_type: ActionType,
        contact_index: int = 0,
        note: str = "",
    ) -> str:
        program = await self._get_program()

        tx = await program.rpc["register_action"](
            ACTION_TYPE_U8.get(action_type, 0),
            contact_index,
            ctx=Context(
                accounts={
                    "event_log": Pubkey.from_string(event_pda),
                    "signer": self._keypair.pubkey(),
                }
            ),
        )

        tx_str = str(tx)
        suffix = f" idx={contact_index}" if action_type == ActionType.NOTIFIED_CONTACT else ""
        note_str = f' note="{note[:40]}"' if note else ""
        print(f"[Solana] register_action {action_type.value}{suffix}{note_str} → tx={tx_str[:16]}...")
        return tx_str

    async def confirm_wellbeing(self, event_pda: str) -> str:
        program = await self._get_program()

        tx = await program.rpc["confirm_wellbeing"](
            ctx=Context(
                accounts={
                    "event_log": Pubkey.from_string(event_pda),
                    "signer": self._keypair.pubkey(),
                }
            ),
        )

        tx_str = str(tx)
        print(f"[Solana] confirm_wellbeing → tx={tx_str[:16]}...")
        return tx_str
