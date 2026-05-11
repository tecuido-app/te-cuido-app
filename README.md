# TE CUIDO

Intelligent preventive care system for elderly adults living alone.

Detects falls, bradycardia, and hypoxia. Automatically escalates alerts to trusted contacts. Logs every action immutably on Solana.

> Hackathon DEV3PACK · May 2026

---

## Deploy online

Agent on **Railway**, dashboard on **Vercel**. Both deploy directly from this repo.

### 1 — Agent → Railway

1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
2. Select this repo, set **Root Directory** to `agent`
3. Railway auto-detects the Dockerfile and builds it
4. In **Variables**, add all keys from `.env.example` (except `NEXT_PUBLIC_*`)
5. Once deployed, copy the public URL Railway assigns (e.g. `https://te-cuido-agent.up.railway.app`)

### 2 — Dashboard → Vercel

1. Go to [vercel.com](https://vercel.com) → New Project → Import from GitHub
2. Set **Root Directory** to `dashboard`
3. In **Environment Variables**, add:
   - `NEXT_PUBLIC_AGENT_URL` = the Railway URL from step 1 (e.g. `https://te-cuido-agent.up.railway.app`)
4. Deploy — Vercel assigns a public URL automatically

### 3 — Test it

```bash
# Hit your live agent
AGENT_URL=https://te-cuido-agent.up.railway.app ./demo.sh status

# Trigger an event from anywhere
AGENT_URL=https://te-cuido-agent.up.railway.app ./demo.sh low_hr --watch
```

---

## Local deploy

```bash
./start.sh
```

Creates `.env` on first run, then builds and starts both containers with Docker Compose.

- Dashboard: http://localhost:3000
- Agent API: http://localhost:8000

**Prerequisites:** Docker and Docker Compose installed.

---

## Configuration

Open `.env` and fill in:

| Variable | Where to get it |
|---|---|
| `GEMINI_API_KEY` | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| `TELEGRAM_BOT_TOKEN` | Create a bot with [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID_CONTACT_1` | Send `/start` to your bot, then call `/getUpdates` |
| `PROGRAM_ID` | Deploy the Solana contract (see `solana/README.md`); set `USE_MOCK_SOLANA=true` to skip |

---

## Demo

Use `demo.sh` to trigger events with colored output:

```bash
./demo.sh fall             # trigger fall
./demo.sh low_hr           # trigger bradycardia
./demo.sh low_spo2         # trigger hypoxia
./demo.sh fall --watch     # trigger + poll status every 3s
./demo.sh reset            # confirm patient wellbeing
./demo.sh status           # check current state

# Target a remote server
AGENT_URL=http://your-server:8000 ./demo.sh low_hr --watch
```

Makefile shortcuts: `make demo-fall`, `make demo-low-hr`, `make demo-low-spo2`, `make reset`.

See [DEMO.md](DEMO.md) for the full pitch script.

---

## Architecture

```
POST /api/simulate
       ↓
  Agent (FastAPI)
  ├── AI Filter (Gemini 2.5 Flash) — dismisses false positives
  ├── Escalation — 60s grace period → Telegram → emergency
  ├── Notifier — Telegram to trusted contacts
  └── Solana Writer — immutable on-chain audit log
              ↓
    Dashboard (Next.js 16)
    ├── Polls /api/agent-status every 3s
    ├── Shows countdown, action timeline, tx hashes
    └── "Patient is fine" button → POST /api/wellbeing
```

---

## Stack

| Layer | Technology |
|---|---|
| Agent | Python 3.11, FastAPI, anchorpy |
| AI filter | Gemini 2.5 Flash |
| Notifications | python-telegram-bot |
| Dashboard | Next.js 16, React 19, Tailwind v4, shadcn/ui |
| Smart contract | Anchor (Rust), Solana devnet |
| Program ID | `FL87A7UXXJGwj8ra3RYUNHHSBSdp9ML3VL9TjfMBpMWN` |

---

## Escalation flow

```
Event detected
  → Gemini evaluates (real or false positive?)
  → If real: 60s grace period
      → No response: Telegram to contact 1
      → No response (180s): Telegram to contact 2
      → No response (180s): emergency
  → Every step logged on-chain in Solana
```

---

## Telegram setup

1. Create a bot with [@BotFather](https://t.me/BotFather) → get the token
2. Each contact sends `/start` to the bot
3. Get their chat ID:
```bash
curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
```

---

## Solana (optional)

The contract is deployed on devnet. The agent wallet is auto-generated at `.solana-wallet.json` (gitignored). To fund it:
- [faucet.solana.com](https://faucet.solana.com) — use the address printed by the agent on startup.

Set `USE_MOCK_SOLANA=true` to skip on-chain writes entirely (generates convincing fake tx hashes — good for demos).

See `solana/README.md` for deploy instructions.

---

## Smart contract

```
solana/lib.rs    — Anchor contract
solana/idl.json  — IDL for the Python client
```

Instructions: `register_event`, `register_action`, `confirm_wellbeing`.  
PDA: `["event", event_id_u64_le]`

---

## Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
make test
# or: python -m pytest -v
```

Tests cover:
- `test_detector.py` — threshold logic, fall detection, throttling
- `test_api.py` — all HTTP endpoints via FastAPI `TestClient`
- `test_escalation.py` — escalation flow with mocked AI, Solana, and Telegram

---

## Versioning

Current version is tracked in [VERSION](VERSION) and `dashboard/package.json`.

```bash
make bump-patch   # 0.1.0 → 0.1.1
make bump-minor   # 0.1.0 → 0.2.0
make bump-major   # 0.1.0 → 1.0.0
```

Each bump commits the version files and creates a git tag (`v0.1.1`, etc.) automatically.

---

## Local development (without Docker)

```bash
# 1. Set up environment
cp .env.example .env
# Fill in .env

# 2. Agent
cd agent && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --reload --port 8000

# 3. Dashboard (separate terminal)
cd dashboard && npm install && npm run dev
```

---

## Project structure

```
te-cuido/
├── agent/
│   ├── tests/      pytest suite (detector, api, escalation)
│   └── ...         FastAPI, detector, escalation, Solana, Telegram
├── dashboard/      Next.js 16 — real-time monitoring UI
├── solana/         Anchor smart contract (Rust) + IDL
├── hardware/       Arduino simulation (TinkerCAD)
├── .env.example    Configuration template
├── docker-compose.yml
├── start.sh        One-command deploy
├── demo.sh         Demo script with parameters
├── pyproject.toml  pytest + bumpversion config
├── VERSION         Current version
├── Makefile        Convenience commands
└── DEMO.md         Pitch script
```
