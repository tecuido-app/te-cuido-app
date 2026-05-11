# Demo Script — TE CUIDO (3 minutes)

## Quick commands

```bash
./demo.sh fall             # trigger fall event
./demo.sh low_hr           # trigger bradycardia
./demo.sh low_spo2         # trigger hypoxia
./demo.sh fall --watch     # trigger + poll status every 3s
./demo.sh reset            # confirm patient wellbeing
./demo.sh status           # check current state

# Target a remote server
AGENT_URL=http://your-server:8000 ./demo.sh low_hr --watch
```

---

## Pre-flight (5 min before the pitch)

- [ ] Both containers running: `./start.sh`
- [ ] Browser open at `http://localhost:3000`
- [ ] Tab open with [Solana Explorer devnet](https://explorer.solana.com/?cluster=devnet)
- [ ] Telegram on a team member's phone (if configured)
- [ ] Terminal ready with `./demo.sh` command
- [ ] Pre-recorded 60s fallback video open in another tab (plan B)

---

## Script

### 0:00–0:20 — The problem

> *"Carmen is 78. Her daughter Juliana works and lives with the guilt of not always being there. The Ato device runs out every time she leaves. People pay for these systems — but they don't exist here."*

### 0:20–1:00 — System active

> Show the dashboard in green.
> *"This is what Juliana sees. Carmen is fine. The system monitors vital signs in real time."*

> Point to the numbers updating every 5 seconds.
> *"Data updates on its own — nothing to do, just watch."*

### 1:00–2:10 — The emergency

> *"But today at 2:32 PM, the system detects a critical heart rate."*

> **Run:**
> ```bash
> ./demo.sh low_hr --watch
> ```

> In the agent terminal you'll see:
> - `[AIFilter]` evaluating with Gemini — "dangerously low heart rate"
> - `[MOCK SOLANA]` transaction hash
> - Status changes to `alert`

> **On the dashboard**, the countdown appears automatically.
> *"First step: 60 seconds for Carmen to confirm she's okay."*

> If the countdown reaches zero or you force it with DevMode → EMERGENCY state.
> *"No response. The agent notifies Juliana via Telegram."*

> If Telegram is configured → show the phone vibrating.

> *"And all of this is signed on Solana."*
> Open the Explorer tab and show the transactions.

### 2:10–2:40 — Close

> *"This is not an alarm. It's an agent that acts, decides, and leaves a forensic record. Today."*

> 2-second pause.

> *"Te Cuido. Intelligent preventive care system for those who matter most."*

---

## Plan B — if Solana devnet is down

- `USE_MOCK_SOLANA=true` in `.env` is the default — the agent keeps working and generates convincing mock tx hashes
- Open real Explorer URLs before the pitch and keep them in tabs

## Plan C — if the agent won't start

- Use only the dashboard with DevMode (bottom right corner) to show the full UX flow
- DevMode cycles ok → alert → emergency without waiting for timers
