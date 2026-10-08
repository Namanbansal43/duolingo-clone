# Duolingo Clone

A full-stack Duolingo-style learning app built for an SDE assignment.

| Part | Stack | Status |
| --- | --- | --- |
| `frontend/` | Next.js 16 (App Router, TypeScript), Tailwind CSS v4 | Landing page done |
| `backend/` | Python 3.12+, FastAPI, SQLAlchemy 2, Alembic, SQLite | Full database schema; `/me` and `/courses` API |

## Running the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:create_app --factory --reload   # http://localhost:8000, API docs at /docs
```

On startup the API applies any pending migrations and inserts missing seed data, so there is no separate setup
step. Other commands, run from `backend/`:

| Command | What it does |
| --- | --- |
| `pytest` | Run the test suite (each test gets its own temporary database) |
| `ruff check . && ruff format --check .` | Lint and format check |
| `python -m app.seed --reset` | Wipe the database, including all progress, and seed it again |
| `alembic revision --autogenerate -m "..."` | Create a migration after changing a model |

Settings come from environment variables or `backend/.env`; see `backend/.env.example`.

## Running the frontend

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

## Database

16 tables covering course content, learner progress, lesson history, XP and achievements. The ER diagram,
the rules the database enforces and the design decisions are in [docs/DATABASE.md](docs/DATABASE.md).

## The logged-in learner

The brief asks us to assume a logged-in user, so there is no sign-up or login. The seed creates one learner
(`alex`), and every API request acts as them: the `get_current_user` dependency in `backend/app/deps.py` is the
only code that decides who "me" is. Adding real authentication would mean replacing that one function.

On a shared demo deployment, every visitor therefore sees and changes the same learner.

## API so far

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Liveness check, including the database |
| GET | `/api/v1/me` | The learner with live stats: hearts after regeneration, streak as of today |
| PATCH | `/api/v1/me` | Set the active course, daily goal (10/20/30/50 XP) or time zone |
| GET | `/api/v1/courses` | All courses in display order; only Spanish is available |

Errors always have the shape `{"error": {"code": "...", "message": "...", "details": ...}}`.

## Brand assets

The logo, flags, illustrations and animations in `frontend/public/landing/` are Duolingo's own artwork. They are
used here only to reproduce the look of duolingo.com for a non-commercial assignment, and remain the property of
Duolingo, Inc. This project is not affiliated with Duolingo. To rebrand, replace that folder; no code changes are
needed.

Duolingo's typefaces are proprietary, so the app uses Signika and Fredoka from Google Fonts as stand-ins.
