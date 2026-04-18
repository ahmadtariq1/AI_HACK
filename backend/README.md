# Backend — FastAPI

A production-ready **FastAPI** backend template wired for the React (Vite) frontend.

---

## Project Structure

```
backend/
├── main.py                     # FastAPI app, CORS, router mount
├── requirements.txt
├── .env                        # environment variables (git-ignored secrets)
├── .gitignore
└── app/
    ├── core/
    │   ├── config.py           # pydantic-settings — reads .env
    │   ├── database.py         # SQLAlchemy engine + get_db dependency
    │   └── security.py         # JWT creation/decoding + bcrypt helpers
    ├── api/
    │   └── v1/
    │       ├── router.py       # top-level v1 router
    │       └── endpoints/
    │           ├── auth.py     # POST /auth/login, /auth/logout
    │           ├── users.py    # CRUD  /users
    │           └── items.py    # CRUD  /items  (example entity — rename me)
    ├── models/
    │   ├── user.py             # SQLAlchemy User ORM model
    │   └── item.py             # SQLAlchemy Item ORM model
    ├── schemas/
    │   ├── auth.py             # Token response schema
    │   ├── user.py             # UserCreate / UserRead / UserUpdate
    │   └── item.py             # ItemCreate / ItemRead / ItemUpdate
    ├── services/
    │   └── user_service.py     # Business logic layer (separate from routes)
    └── utils/
        └── helpers.py          # Shared utilities
```

---

## Quick Start

```bash
# 1 — create & activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 2 — install dependencies
pip install -r requirements.txt

# 3 — edit .env (set SECRET_KEY, DATABASE_URL, etc.)
cp .env .env.local              # optional: local overrides

# 4 — run the dev server  (hot-reload enabled)
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## CORS

The React Vite dev server runs on **http://localhost:5173** — already in `ALLOWED_ORIGINS`.  
Add your production domain in `.env` or `app/core/config.py` before deploying.

---

## Adding a New Resource

1. **Model** — add `app/models/my_entity.py` (SQLAlchemy class)
2. **Schema** — add `app/schemas/my_entity.py` (Pydantic BaseModel)
3. **Service** — add `app/services/my_entity_service.py` (DB queries)
4. **Endpoints** — add `app/api/v1/endpoints/my_entity.py` (FastAPI router)
5. **Register** — import and include the router in `app/api/v1/router.py`

---

## Database Migrations (Alembic)

```bash
# initialise (first time only)
alembic init alembic

# generate a migration from model changes
alembic revision --autogenerate -m "create users table"

# apply migrations
alembic upgrade head
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PROJECT_NAME` | `AI Hack API` | API title shown in docs |
| `ENVIRONMENT` | `development` | `development` / `production` |
| `API_V1_STR` | `/api/v1` | API prefix |
| `DATABASE_URL` | `sqlite:///./dev.db` | SQLAlchemy connection string |
| `SECRET_KEY` | *(change me!)* | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token TTL in minutes |
| `ALLOWED_ORIGINS` | `["http://localhost:5173"]` | CORS allowed origins |
