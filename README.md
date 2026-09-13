# ASTRA AI Agent OS

ASTRA is a local-first agent operating layer with a desktop control surface. It includes a FastAPI agent core, persistent task and memory storage, policy-gated tools, audit logs, and a React dashboard with browser voice input/output.

## Run locally

```powershell
# Terminal 1
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend defaults to `http://localhost:8000` for the API.

## Safety model

Tools are classified as `read`, `confirm`, or `blocked`. Destructive and externally visible actions need a confirmation token. The included adapters are deliberately conservative and log every request; add platform-specific integrations only behind the same policy boundary.

## Layout

- `backend/` — API, orchestration loop, memory, policy engine, and tool adapters
- `frontend/` — ASTRA desktop UI and browser voice controls
