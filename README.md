# Duolingo Clone

A full-stack Duolingo-style learning app built for an SDE assignment.

| Part | Stack | Status |
| --- | --- | --- |
| `frontend/` | Next.js 16 (App Router, TypeScript), Tailwind CSS v4 | Landing page, "Get started" flow, `/learn` |
| `backend/` | Python 3.12+, FastAPI, SQLAlchemy 2, Alembic, SQLite | Full schema, seeded Spanish course; learner, course and path API |

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

Troubleshooting:

- **Activate the virtual environment in every new terminal** (`.venv\Scripts\activate`; the prompt then starts
  with `(.venv)`). Otherwise a globally installed `uvicorn` may run without the project's packages and fail with
  `ModuleNotFoundError`. Alternatively, skip activation and run `.venv\Scripts\python -m uvicorn ...`.
- **`[WinError 10013]` or "address already in use"** means something is already listening on port 8000, usually
  an earlier backend still running. Stop it, or start this one with `--port 8001` and point the frontend at it
  with `API_URL=http://localhost:8001` in `frontend/.env.local`.

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
| `/learn` | The learning path, inside the app shell (below) |

### "Get started" flow

Every "Get started" button on the landing page opens `/welcome`, three screens modelled on duolingo.com's
own onboarding and measured against it at 1280×800:

1. **"I want to learn..."**: every course from `GET /api/v1/courses`, with the real number of learners
   studying it. Only Spanish has content; the other courses show a "coming soon" message.
2. **"Hi there! I'm Duo!"**: Duo waves (Duolingo's own Lottie animation).
3. **"What's your daily learning goal?"**: 5, 10, 15 or 20 minutes a day. Duolingo stores these as 10, 20, 30
   and 50 XP, and so does this app. The choices are native radio buttons, so arrow keys and Enter work.

Nothing is saved until the last CONTINUE, which sends one `POST /api/v1/me/onboarding` with the course, the daily
goal and the browser's time zone (so streak days follow the learner's own midnight), then opens `/learn`. Signing
up means a new account, so the learner starts over: their history and stats are cleared, and the path begins at
its first node. "I already have an account" goes straight to `/learn` and keeps the learner as they are, since the
learner is always logged in.

Duolingo's flow also asks how you heard about it, why you are learning, how much you already know, and for
notification permission. Those screens are left out: nothing in this app would use the answers.

### `/learn`: the app shell and the learning path

Measured against duolingo.com's own `/learn` page (opened as a guest) at 1280, 1024, 800 and 390 px wide.

- **App shell**, shared by every signed-in page (`frontend/src/app/(app)/layout.tsx`): a left sidebar with
  Learn, Leaderboards, Quests, Shop, Profile and More. It is 256 px wide with labels from 1160 px, icons only
  below that, and becomes a bottom tab bar on phones. Pages that aren't built yet show a "coming soon" message.
- **Right rail** (1024 px and up; a stats bar across the top below that): course flag, streak, gems and hearts
  from `GET /api/v1/me` (switching courses is "coming soon", as only Spanish has content); an "Unlock Leaderboards!" card counting down the 10 lessons that open leaderboards; and
  the daily quest, which tracks today's XP against the daily goal.
- **The path** (`GET /api/v1/courses/{id}/path`): units in order, each with a sticky green header that follows
  the unit being scrolled through, and nodes that snake left and right at Duolingo's offsets (0, 45 and 70 px).
  Completed nodes show a check, the next one has a progress ring and a bouncing START bubble, and the rest are
  grey. A trophy ends each unit, and Duo stands beside the path (greyed-out characters beside locked units).
- **Node popovers**: the next node offers "Start +10 XP"; locked nodes explain what unlocks them. Lessons arrive
  with the lesson player, so START shows a "coming soon" message for now.
- **Treasure chests** open with one tap once reached (`POST /api/v1/skills/{id}/open-chest`): 20 gems, and the
  next node unlocks.

### Game rules so far

| Rule | Value | Where |
| --- | --- | --- |
| Path order | Nodes unlock strictly one after another, across units; only completion is stored | `backend/app/services/path.py` |
| Lesson XP | 10 XP per lesson | `backend/app/services/rules.py` |
| Chest | 20 gems, once | `backend/app/services/rules.py` |
| Hearts | 5 at most; one comes back every 30 minutes (`HEART_REGEN_MINUTES`) | `backend/app/services/hearts.py` |
| Streak | Counts days with a finished lesson, in the learner's time zone; reads 0 after a missed day | `backend/app/services/streak.py` |
| Daily goal | 10, 20, 30 or 50 XP (shown as 5, 10, 15, 20 minutes) | `backend/app/models/learner.py` |
| Leaderboards | Open after 10 finished lessons | `frontend/src/components/app/right-rail.tsx` |
| New learner | Starts at the first node with 500 gems, 5 hearts, no XP and no streak | `backend/app/services/learner.py` |

### Demo data

The seeded learner starts partway through Unit 1, so every node state is visible straight away: "Say hello"
finished, "Introduce yourself" at lesson 2 of 3, and the rest locked. Behind that are 4 real lessons on the 3
days before the database was first seeded: sessions, XP events, 40 XP and a 3-day streak that today's first lesson
would extend. This is the learner that "I already have an account" opens. Finishing "Get started" replaces them
with a brand-new learner at the first node; `python -m app.seed --reset` restores this starting point.

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
| GET | `/api/v1/me` | The learner with live stats: hearts after regeneration, streak and XP as of today |
| PATCH | `/api/v1/me` | Set the active course, daily goal (10/20/30/50 XP) or time zone, keeping progress |
| POST | `/api/v1/me/onboarding` | Finish "Get started": the learner starts over with the chosen course, goal and time zone |
| GET | `/api/v1/courses` | All courses in display order with learner counts; only Spanish is available |
| GET | `/api/v1/courses/{course_id}/path` | The course's units and nodes, each completed, active or locked |
| POST | `/api/v1/skills/{skill_id}/open-chest` | Open the treasure chest the learner has reached (+20 gems) |

Every request and response, with real examples and every error code, is documented in
[docs/API.md](docs/API.md). With the backend running, `/docs` serves the same reference interactively.
Errors always have the shape `{"error": {"code": "...", "message": "...", "details": ...}}`.

## Brand assets

The logo, flags, icons, illustrations and animations in `frontend/public/landing/`, `frontend/public/onboarding/`
and `frontend/public/app/` are Duolingo's own artwork (the lit streak flame, the white trophy and the check
mark are recoloured or drawn here). They are used here only to reproduce the look of duolingo.com for a non-commercial
assignment, and remain the property of Duolingo, Inc. This project is not affiliated with Duolingo. To rebrand,
replace those folders; no code changes are needed.

Animations play through lottie-web's "light" player, which renders SVG and never runs the scripts some animation
files can carry. Each one has a still SVG poster, shown while it loads and to visitors who prefer reduced motion.

Duolingo's typefaces are proprietary, so the app uses Signika and Fredoka from Google Fonts as stand-ins.
