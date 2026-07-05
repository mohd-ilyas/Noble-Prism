# Noble Prism — Agent-to-Agent Payment Protocol

> Production-grade backend for autonomous machine-to-machine payments.

---

## Quick Start

### Docker (recommended — one command)

```bash
cd noble-prism-main
docker compose up --build
```

- **Backend API:** http://localhost:8000
- **Swagger docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

The backend automatically:
1. Waits for PostgreSQL to be healthy
2. Creates all database tables
3. Seeds demo data (6 agents, 7 transactions, 6 policies, ledger entries, audit logs)

---

## Local Development (no Docker)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

SQLite fallback is used automatically when PostgreSQL is unavailable.

---

## Running Tests

```bash
cd backend
pip install pytest httpx
pytest tests/ -v
```

---

## Frontend Integration

Add to your `.env` (or `.env.local`):

```env
VITE_API_URL=http://localhost:8000
```

The frontend ships with a complete API client at `src/lib/api.ts`.

---

## Production Deployment

Render deployment is defined in `../render.yaml`.

Required production secrets must be configured in the Render dashboard:

- `DATABASE_URL` pointing to Supabase PostgreSQL.
- `CORS_ORIGINS` set to the deployed frontend origin.
- `OPENROUTER_API_KEY` for backend-only AI calls.

Copy `backend/.env.example` for backend settings and `../.env.example` for frontend settings during local setup. Do not commit real `.env` files.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/agents` | List all registered agents |
| POST | `/agents/register` | Register a new agent |
| GET | `/agents/{id}` | Get agent by ID or name |
| GET | `/policies` | List all policies |
| POST | `/policies` | Create a policy |
| PUT | `/policies/{id}` | Update a policy |
| POST | `/transactions/evaluate` | Dry-run evaluation (no persistence) |
| POST | `/transactions/initiate` | Full authorization pipeline |
| POST | `/transactions/approve` | Human approval of escalated tx |
| POST | `/transactions/reject` | Human rejection of escalated tx |
| GET | `/ledger` | Tamper-evident settlement ledger |
| GET | `/insights` | KPIs, volume series, AI insights |
| POST | `/killswitch/activate` | Freeze an agent |
| POST | `/killswitch/release` | Release a frozen agent |
| GET | `/health` | Service health check |

---

## Demo Scenarios

### Scenario 1 — GPU Compute Approved

```bash
curl -X POST http://localhost:8000/transactions/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "openai-buyer-07",
    "to": "aws-c-broker",
    "amount": 18.0,
    "currency": "USD",
    "category": "gpu_compute",
    "purpose": "H100 GPU compute lease"
  }'
```

**Expected:** `decision: "approved"`, `intent_score: 96`, `risk_score: < 0.10`

---

### Scenario 2 — Crypto Mining Blocked (RULE 1)

```bash
curl -X POST http://localhost:8000/transactions/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "openai-buyer-07",
    "to": "crypto-mining-market",
    "amount": 5000.0,
    "currency": "USD",
    "category": "mining",
    "purpose": "Crypto Mining Hardware"
  }'
```

**Expected:** `decision: "blocked"`, `intent_score: 4`, `reason: "intent mismatch"`

---

### Scenario 3 — Velocity Kill Switch (RULE 3)

```bash
# Fire 20 rapid transactions using the initiate endpoint
for i in $(seq 1 20); do
  curl -s -X POST http://localhost:8000/transactions/initiate \
    -H "Content-Type: application/json" \
    -d '{"from":"anthropic-broker","to":"aws-c-broker","amount":1.0,"category":"gpu_compute","purpose":"test"}'
done
# Check agent status
curl http://localhost:8000/agents/anthropic-broker
```

**Expected:** Agent status `offline`, `is_frozen: true`, kill-switch event created.

---

### Scenario 4 — Human Approval Required (RULE 2)

```bash
curl -X POST http://localhost:8000/transactions/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "from": "anthropic-broker",
    "to": "aws-c-broker",
    "amount": 4999.0,
    "currency": "USD",
    "category": "gpu_compute",
    "purpose": "Large GPU batch"
  }'
```

**Expected:** `decision: "human_approval_required"`

---

## Architecture

```
POST /transactions/initiate
         │
         ▼
  Identity Lookup          — is agent registered and not frozen?
         │
         ▼
  Velocity Check           — count tx in rolling window (RULE 3)
         │
         ▼
  Intent Engine            — category in allowed list? (RULE 1)
         │
         ▼
  Policy Engine            — daily limit, per-tx limit
         │
         ▼
  Risk Engine              — multi-factor fraud score 0.0–1.0
         │
         ▼
  Approval Threshold       — amount > threshold? (RULE 2)
         │
         ▼
  Settlement               — ledger append + audit log (RULE 4)
```

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `agents` | Identity, wallet, reputation, freeze state |
| `policies` | Per-agent spending rules and category allowlists |
| `transactions` | Every authorization attempt with full decision data |
| `ledger_entries` | Hash-chained settlement receipts |
| `audit_logs` | Immutable event stream |
| `kill_switch_events` | Agent freeze/release history |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./nobleprism.db` | PostgreSQL or SQLite URL |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed frontend origins |
| `VELOCITY_WINDOW_SECONDS` | `120` | Rolling window for velocity check |
| `VELOCITY_MAX_TRANSACTIONS` | `20` | Kill-switch threshold |
| `KILL_SWITCH_RISK_THRESHOLD` | `0.85` | Auto-escalate above this risk score |
| `ENVIRONMENT` | `development` | Environment label |
| `OPENROUTER_API_KEY` | empty | Backend-only OpenRouter credential |
| `OPENROUTER_MODEL` | `deepseek/deepseek-chat-v3` | Default AI model |
| `OPENROUTER_TIMEOUT_SECONDS` | `12` | Provider call timeout |
| `OPENROUTER_MAX_RETRIES` | `2` | Retry count for transient provider errors |
