# LangGraph-FoundryIQ API

FastAPI service that exposes a **LangGraph** agent which calls the Microsoft **Foundry agent (`sp-search`)** through the **APIM AI Gateway**.

## Run locally

```powershell
cd api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # fill in APIM key / Foundry endpoint
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Method | Path                  | Description                                          |
|--------|-----------------------|------------------------------------------------------|
| GET    | `/health`             | Liveness probe                                       |
| GET    | `/ready`              | Readiness probe                                      |
| GET    | `/api/v1/prompts`     | Returns the 10 sample prompts shown in the UI        |
| POST   | `/api/v1/chat`        | Sends a prompt through the LangGraph → Foundry flow  |

Sample chat request:

```bash
curl -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\":\"What are our latest company policies on remote work?\"}"
```

## How the call flows

```
UI  ─►  /api/v1/chat  ─►  LangGraph (prepare → invoke_foundry → enrich → finalize)
                                  │
                                  ▼
                       APIM AI Gateway (private VNET)
                                  │
                                  ▼
                       Foundry Agent  sp-search
                                  │
                                  ▼
                       Foundry IQ → Azure AI Search (sp-search-index)
```
