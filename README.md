# Duolingo Clone

A full-stack Duolingo-style learning app built for an SDE assignment.

| Part | Stack | Status |
| --- | --- | --- |
| `frontend/` | Next.js 16 (App Router, TypeScript), Tailwind CSS v4 | Landing page, "Get started" flow |
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

Start the backend first: every page after the landing page reads from it. The browser only ever calls `/api/...`
on the frontend's own origin, and Next.js forwards those requests to the backend (a rewrite in
`frontend/next.config.ts`), so there is no CORS to set up and no backend URL in client code. The backend URL
defaults to `http://localhost:8000`; set `API_URL` (see `frontend/.env.example`) to point elsewhere.

| Command (from `frontend/`) | What it does |
| --- | --- |
| `npm run dev` | Development server with hot reload |
| `npm run build` | Production build (type-checks too) |
| `npm run lint` | ESLint |

## Pages

| Path | What it is |
| --- | --- |
| `/` | Landing page, matching duolingo.com section by section |
| `/welcome` | The "Get started" flow (below) |
| `/learn` | Temporary: shows what the flow saved. The learning path replaces it. |

### "Get started" flow

Every "Get started" button on the landing page opens `/welcome`, three screens modelled on duolingo.com's
own onboarding and measured against it at 1280×800:

1. **"I want to learn..."**: every course from `GET /api/v1/courses`, with the real number of learners
   studying it. Only Spanish has content; the other courses show a "coming soon" message.
2. **"Hi there! I'm Duo!"**: Duo waves (Duolingo's own Lottie animation).
3. **"What's your daily learning goal?"**: 5, 10, 15 or 20 minutes a day. Duolingo stores these as 10, 20, 30
   and 50 XP, and so does this app. The choices are native radio buttons, so arrow keys and Enter work.

Nothing is saved until the last CONTINUE, which sends one `PATCH /api/v1/me` with the course, the daily goal and
the browser's time zone (so streak days follow the learner's own midnight), then opens `/learn`. "I already have
an account" goes straight to `/learn`, since the learner is always logged in.

Duolingo's flow also asks how you heard about it, why you are learning, how much you already know, and for
notification permission. Those screens are left out: nothing in this app would use the answers.

## Database

16 tables covering course content, learner progress, lesson history, XP and achievements. The ER diagram,
the rules the database enforces and the design decisions are in [docs/DATABASE.md](docs/DATABASE.md).

## The logged-in learner

The brief asks us to assume a logged-in user, so there is no sign-up or login. The seed creates one learner
(`alex`), and every API request acts as them: the `get_current_user` dependency in `backend/app/deps.py` is the
only code that decides who "me" is. Adding real authentication would mean replacing that one function.

On a shared demo deployment, every visitor therefore sees and changes the same learner.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Liveness check, including the database |
| GET | `/api/v1/me` | The learner with live stats: hearts after regeneration, streak as of today |
| PATCH | `/api/v1/me` | Set the active course, daily goal (10/20/30/50 XP) or time zone |
| GET | `/api/v1/courses` | All courses in display order with learner counts; only Spanish is available |

Every request and response, with real examples and every error code, is documented in
[docs/API.md](docs/API.md). With the backend running, `/docs` serves the same reference interactively.
Errors always have the shape `{"error": {"code": "...", "message": "...", "details": ...}}`.

## Brand assets

The logo, flags, illustrations and animations in `frontend/public/landing/` and `frontend/public/onboarding/` are
Duolingo's own artwork. They are used here only to reproduce the look of duolingo.com for a non-commercial
assignment, and remain the property of Duolingo, Inc. This project is not affiliated with Duolingo. To rebrand,
replace those folders; no code changes are needed.

Animations play through lottie-web's "light" player, which renders SVG and never runs the scripts some animation
files can carry. Each one has a still SVG poster, shown while it loads and to visitors who prefer reduced motion.

Duolingo's typefaces are proprietary, so the app uses Signika and Fredoka from Google Fonts as stand-ins.
