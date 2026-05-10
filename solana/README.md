# Smart Contract — TE CUIDO

Anchor program que guarda cada acción del agente como audit log inmutable on-chain.

## Deploy en Solana Playground (sin instalar nada local)

1. Abrí **https://beta.solpg.io**
2. Crear nuevo proyecto: botón **"Create"** → **Anchor**
3. Pegá todo el contenido de `lib.rs` en el editor (reemplaza el ejemplo por defecto)
4. Click **"Build"** abajo a la izquierda — debería compilar en ~30 segundos
5. Click **"Deploy"** — Playground te da SOL gratis automáticamente
6. Copiá el **Program ID** que aparece en consola (algo como `7xKp9mZqA...`)
7. Pegá el Program ID en:
   - Línea 11 de `lib.rs`: cambiá `declare_id!("11111111111111111111111111111111")` por tu ID real
   - `.env` del proyecto (raíz): `PROGRAM_ID=...` y `NEXT_PUBLIC_PROGRAM_ID=...`
8. Hacé **Build** + **Deploy** otra vez (necesario después de cambiar `declare_id!`)
9. Descargá el IDL: tab **"IDL"** → **"Download"** → guardalo como `solana/idl.json`

Listo. El contrato está vivo en devnet.

## Verificar que funciona

En Playground, tab **"Test"** o **"Anchor"** → **Instructions**:
- Probá `register_event` con `event_id=12345`, `event_type=0` (Fall), `severity=3`, `value=600`
- Debería devolver una transacción exitosa
- Mirá la cuenta creada en el Explorer

## Instrucciones del programa

| Instrucción | Args | Quién firma |
|---|---|---|
| `register_event` | `event_id (u64)`, `event_type (u8)`, `severity (u8)`, `value (i64)` | agente |
| `register_action` | `action_type (u8)`, `contact_index (u8)` | agente |
| `confirm_wellbeing` | (sin args) | agente (en MVP — en prod, el familiar) |

## Códigos numéricos (sin enums para simplicidad de cliente)

**EventType:**
- `0` = Fall (caída)
- `1` = LowHR (bradicardia)
- `2` = LowSpO2 (hipoxia)

**ActionType:**
- `0` = GracePeriod (ventana 60s)
- `1` = AIDismissed (descartado por IA como falso positivo)
- `2` = NotifiedContact (Telegram enviado)
- `3` = Escalated (escalado a emergencia)
- `4` = WellbeingConfirmed (familiar confirmó OK)
- `5` = Resolved (cerrado)

## PDA del EventLog

```
seeds = [b"event", event_id_le_bytes(8)]
```

`event_id` lo genera el cliente (ej: `int(time.time() * 1000)`). Garantiza unicidad por timestamp.

## Próximo paso (solana_writer.py)

Una vez deployado el programa y guardado el IDL, escribir `agent/solana_writer.py` usando [anchorpy](https://github.com/kevinheavey/anchorpy):

```python
from anchorpy import Program, Provider, Wallet
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient

# Cargar IDL desde solana/idl.json
# Construir Program(idl, program_id, provider)
# Llamar program.rpc["register_event"](event_id, event_type, ...)
```

(Para hackathon, Flor puede dejar el `MockSolanaWriter` en producción si el deploy no llega — el dashboard ya mostrará tx hashes mock que se ven creíbles.)
