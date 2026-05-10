# TE CUIDO

Sistema preventivo inteligente para el cuidado de adultos mayores que viven solos.

Detecta caídas, bradicardia e hipoxia. Escala automáticamente a contactos de confianza. Registra cada acción de forma inmutable en Solana.

> Hackathon DEV3PACK · Mayo 2026

---

## Demo en vivo

**Terminal 1 — agente (WSL)**
```bash
cd /mnt/c/Users/<usuario>/te-cuido
source agent/venv/bin/activate
uvicorn agent.api:app --port 8000
```

**Terminal 2 — dashboard (PowerShell)**
```powershell
cd dashboard
npm start
# → http://localhost:3000
```

**Terminal 3 — disparar evento**
```bash
# Bradicardia
curl -X POST "http://localhost:8000/api/simulate?event_type=low_hr"

# Caída
curl -X POST "http://localhost:8000/api/simulate?event_type=fall"

# SpO2 bajo
curl -X POST "http://localhost:8000/api/simulate?event_type=low_spo2"

# Cancelar escalada ("Carmen está bien")
curl -X POST "http://localhost:8000/api/wellbeing"
```

El dashboard detecta el agente automáticamente y muestra datos en tiempo real.

---

## Arquitectura

```
POST /api/simulate
       ↓
  Agent (FastAPI)
  ├── AI Filter (Gemini 2.5 Flash) — descarta falsos positivos
  ├── Escalation — grace period 60s → Telegram → emergencia
  ├── Notifier — Telegram a contactos de confianza
  └── Solana Writer — audit log inmutable on-chain
              ↓
    Dashboard (Next.js 16)
    ├── Polls /api/agent-status cada 3s
    ├── Muestra countdown, timeline de acciones, txHashes
    └── Botón "Carmen está bien" → POST /api/wellbeing
```

---

## Stack

| Capa | Tecnología |
|---|---|
| Agente | Python 3.12, FastAPI, anchorpy |
| AI filter | Gemini 2.5 Flash |
| Notificaciones | python-telegram-bot |
| Dashboard | Next.js 16, React 19, Tailwind v4, shadcn/ui |
| Smart contract | Anchor (Rust), Solana devnet |
| Program ID | `FL87A7UXXJGwj8ra3RYUNHHSBSdp9ML3VL9TjfMBpMWN` |

---

## Setup

### 1. Variables de entorno

```bash
cp .env.example .env
# Completar GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID_CONTACT_1
```

### 2. Agente (WSL / Linux)

```bash
cd agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Dashboard (Windows / Node.js)

```bash
cd dashboard
npm install
npm run build
```

### 4. Telegram

1. Crear bot con [@BotFather](https://t.me/BotFather) → obtener token
2. El contacto le manda `/start` al bot
3. Obtener su chat_id:
```bash
curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
```

### 5. Solana (opcional — `USE_MOCK_SOLANA=false`)

El contrato está deployado en devnet. El wallet del agente se genera automáticamente en `.solana-wallet.json` (gitignoreado). Para fondear:
- [faucet.solana.com](https://faucet.solana.com) con la dirección que imprime el agente al arrancar.

---

## Flujo de escalada

```
Evento detectado
  → Gemini evalúa (¿real o falso positivo?)
  → Si real: grace period 60s
      → Sin respuesta: Telegram a contacto 1
      → Sin respuesta (180s): Telegram a contacto 2
      → Sin respuesta (180s): emergencia
  → Cada paso registrado on-chain en Solana
```

---

## Smart contract

```
solana/lib.rs    — contrato Anchor
solana/idl.json  — IDL para el cliente Python
```

Instrucciones: `register_event`, `register_action`, `confirm_wellbeing`.  
PDA: `["event", event_id_u64_le]`

Deploy en [Solana Playground](https://beta.solpg.io) → copiar program ID a `.env`.

---

## Estructura

```
te-cuido/
├── agent/          Python — FastAPI, detector, escalation, Solana, Telegram
├── dashboard/      Next.js 16 — UI de monitoreo en tiempo real
├── solana/         Anchor smart contract (Rust) + IDL
├── .env.example    Plantilla de configuración
├── DEMO.md         Script del pitch
└── Makefile        Comandos útiles
```
