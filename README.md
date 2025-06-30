# MCP-Service 🚀

**MCP-Service** is the backend that exposes organization’s tools (Slack, Gmail, Google Calendar, Pensieve, etc.) through the **Model-Context-Protocol (MCP)**.
It lets any OpenAI Agent (or other MCP host) call those tools over Streamable-HTTP and obtain live data for reasoning.

---

## ✨ What this repo gives you

| Feature                                              | Why it matters                                                                |
| ---------------------------------------------------- | ----------------------------------------------------------------------------- |
| **FastMCP server** (`app.main`)                      | Runs the official MCP reference server with FastAPI & Streamable-HTTP         |
| **Tool adapters** (`app/tools/…`)                    | Ready-made wrappers for Slack, Gmail, Calendar, Google Tasks, Pensieve search |
| **Vector store client** (`app/webclients/pensieve/`) | Persists & queries chunks in **Qdrant**                                       |
| **Async Postgres pool**                              | Keeps user-level metadata and refresh tokens                                  |
| **Robust error handling & logging**                  | One place (`logging.ini`) to tweak verbosity                                  |

---

## 🗂️ Repository layout

```
mcp-service/
├── app/
│   ├── main.py              # Entry-point (FastAPI + MCP)
│   ├── tools/               # All @server.tool implementations
│   ├── webclients/          # External API wrappers (Slack, Gmail, Qdrant …)
│   ├── agents/              # Client-side helpers (optional)
│   ├── dto/              # Pydantic models (VectorRequest, PensieveRequest, …)
│   ├── utils/               # Logging, constants, helper fns
│   └── config/              # logging.ini, env var keys, etc.
├── scripts/                 # One-off helpers (DB migrations, data backfill)
├── tests/                   # pytest unit + integration tests
├── .env                     # Template env vars
├── requirements.txt
└── README.md                # ← you are here
```

---

## 🏁 Getting Started (LOCAL DEV)

### 1  Install prerequisites

| Tool                         | Version | Purpose                                         |
| ---------------------------- | ------- | ----------------------------------------------- |
| **Python**                   | 3.11+   | Async & typing goodies                          |
| **PostgreSQL**               | 14+     | Persistent store                                |
| **Qdrant**                   | 1.8+    | Vector DB for Pensieve chunks                   |
| **Poetry** (or `pip`+`venv`) | latest  | Python deps                                     |

### 2  Clone & install

```bash
git clone git@github.com:theved-ai/ved-mcp-service.git
cd mcp-service
cp .env .env                # edit creds & secrets
poetry install              # or: python -m venv venv && pip install -r requirements.txt
```

### 3  Spin up infrastructure

```bash
cd mcp-service
docker-compose up -d
```

### 4  Run migrations / seed data

```bash
poetry run python scripts/init_db.py
```

### 5  Start the MCP server (dev)

```bash
poetry run python app/main.py
# or with live-reload
poetry run uvicorn app.main:fastapi_app --reload
```

### 6  Debugging tips

* Set `LOG_LEVEL=DEBUG` in `.env` for verbose output.

---

## 🧩 Key Concepts

| Concept             | In this repo                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------- |
| **MCP Session**     | Streamable-HTTP transport handled by FastMCP; one session per HTTP request (see `app/main.py`).         |
| **Tool**            | FastMCP `@server.tool` functions (search Gmail, post Slack, search Pensieve, etc.).                     |
| **Pensieve search** | Semantic query that fans out to Qdrant (`vector`) + Postgres (`metadata`).                              |
| **VectorRequest**   | Canonical payload we upsert into Qdrant; timestamps stored as **float Unix seconds** for range filters. |
| **Postgres pool**   | Created once at startup (`init_pg_pool`) and injected where needed.                                     |

---

## 🤝 Contributing

1. **Fork & branch** from `main`.
3. Add/modify **tests** in `tests/` (`pytest -q`).
4. Run `poetry run task lint && poetry run task test` before pushing.
5. Open a PR; the CI will run lint + tests automatically.

Please open issues for bug reports or feature requests.
Happy hacking! 🎉
