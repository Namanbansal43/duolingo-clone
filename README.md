# Duolingo Clone

A full-stack Duolingo-style learning app built for an SDE assignment.

| Part | Stack | Status |
| --- | --- | --- |
| `frontend/` | Next.js 16 (App Router, TypeScript), Tailwind CSS v4 | Landing page, "Get started" flow, `/learn`, lessons, profile |
| `backend/` | Python 3.12+, FastAPI, SQLAlchemy 2, Alembic, SQLite | Full schema, seeded Spanish course; learner, path, lesson and achievement API |

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
| `/lesson` | The lesson being played, full screen (below) |
| `/profile` | The learner's profile: statistics, XP this week, achievements (below) |
| `/profile/achievements` | Every achievement with its progress ("View all") |

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
  from `GET /api/v1/me` (switching courses is "coming soon", as only Spanish has content); an "Unlock
  Leaderboards!" card counting down the 10 lessons that open leaderboards; and the daily quest, which tracks
  today's XP against the daily goal.
- **The path** (`GET /api/v1/courses/{id}/path`): units in order, each with a sticky green header that follows
  the unit being scrolled through, and nodes that snake left and right at Duolingo's offsets (0, 45 and 70 px).
  Completed nodes show a check, the next one has a progress ring and a bouncing START bubble, and the rest are
  grey. A trophy ends each unit, and Duo stands beside the path (greyed-out characters beside locked units).
- **Node popovers**: the next node offers "Start +10 XP", finished ones "Practice +5 XP", and locked nodes say
  what unlocks them. START creates the session (`POST /api/v1/sessions`) and opens `/lesson`; with no hearts left
  it opens the out-of-hearts dialog instead.
- **Treasure chests** open with one tap once reached (`POST /api/v1/skills/{id}/open-chest`): 20 gems, and the
  next node unlocks.

### `/lesson`: the lesson player

Modelled on a real lesson on duolingo.com, played as a guest and measured screen by screen.

- **Layout**: close button, progress bar and hearts across the top; the exercise in a 600 px column; SKIP and
  CHECK along the bottom. CHECK stays grey until there is an answer. After 5 right answers in a row the bar turns
  orange and counts the run ("5 IN A ROW").

Each exercise type has its own view, picked by a small registry (`frontend/src/components/lesson/exercises/`):

| Type | On screen |
| --- | --- |
| Multiple choice | "Select the correct meaning": Duo says a word; pick its meaning from numbered cards |
| Word bank | "Write this in English/Spanish": tap tiles onto the answer lines; used tiles leave a grey gap |
| Match pairs | "Select the matching pairs": two columns, each pair checked as it is tapped |
| Fill in the blank | A sentence with a gap; the chosen word fills it |
| Type the answer | A text box, with keys for á é í ó ú ü ñ ¿ ¡ when the answer is Spanish |
| Listen | "Tap what you hear": the sentence is read aloud (normal speed or slow), rebuilt from tiles |

- **Feedback bar**: slides up green ("Good job!", "Awesome!"...) or red with "Correct solution:". A typed answer
  with one slip or a missing accent counts, with "You have a typo." and the spelling; another accepted
  translation shows "Another correct solution:" with the main one.
- **Mistakes** go to the back of the lesson. When only they are left, Duo says "Let's review the exercise you
  missed!", and each comes back labelled PREVIOUS MISTAKE.
- **Hearts**: a wrong answer, a wrong pair or SKIP costs one in a lesson (never in practice). At 0, the
  out-of-hearts dialog offers a refill for 350 gems, practice to earn one back, or ending the lesson.
- **Quitting** after any progress asks "Wait, don't go! You'll lose your progress if you quit now".
- **The end**: "Lesson complete!" with three cards (XP, accuracy, time), then, for the day's first lesson, the
  streak screen with the flame, the new count and the days around today, then "Achievement unlocked!" for each
  achievement that went up a level, with its badge and what the next level needs.
- **Audio** (a bonus in the brief): Spanish is read aloud with the browser's text-to-speech; speaker buttons
  replay it, and "Can't listen now" skips the listening exercises. Sound effects are synthesised with the Web
  Audio API, so there are no audio files.
- **Keyboard**: number keys pick choices (1-5 and 6-0 in match pairs), Enter checks and continues.
- **Speaking** exercises are left out: the brief allows real speech recognition to stay a placeholder.

The page plays the learner's session in progress (`GET /api/v1/sessions/current`), so a refresh carries on where
it was. Answers are graded only by the server, and the browser never receives the solutions, except the
sentence a listening exercise reads aloud (text-to-speech needs the text).

### `/profile`: profile and achievements

Laid out like a profile on duolingo.com, measured against public profiles there at 1280 px (a guest can't open
their own profile, so the page combines that layout with what only the owner sees: progress towards each
achievement's next level).

- **Header**: Duolingo's empty avatar on a light blue banner, name, username, join month, Following and Followers
  (friends are a placeholder the brief allows, so both are 0 and say "coming soon"), and the course flag.
- **Statistics**: day streak, total XP, current league and top 3 finishes. Leagues arrive with the leaderboard, so
  for now the league reads "None" and there are no top 3 finishes.
- **XP this week**: a line chart of the last 7 days from `GET /api/v1/me/xp-history`, drawn as plain SVG at
  duolingo.com's proportions, with the week's total.
- **Achievements**: a row of badges in Duolingo's artwork, coloured once reached and gold at the top level;
  "View all" opens `/profile/achievements`, which lists each one with its level, a progress bar ("3/7") and the
  next goal. Both read `GET /api/v1/me/achievements`.
- **Right rail**: the stats bar and a Following / Followers card with Duolingo's empty states.

**Where XP shows.** The brief lists XP in the top bar, but duolingo.com's top bar has only the flag, streak, gems
and hearts. To keep that bar identical, total XP is on the profile, today's XP is in the Daily Quests card on
`/learn`, and each lesson's XP is on its result screen.

### Game rules so far

| Rule | Value | Where |
| --- | --- | --- |
| Path order | Nodes unlock strictly one after another, across units; only completion is stored | `backend/app/services/path.py` |
| Content | Unit 1 is playable: 7 lessons with one exercise of each of the 6 types (42 in all); Units 2 and 3 are "coming soon" | `backend/app/seed/spanish.py` |
| Lessons | A lesson node has 2 lessons, a unit review 1; finishing the last completes the node | `backend/app/services/sessions.py` |
| XP | 10 per lesson, 5 per practice session | `backend/app/services/rules.py` |
| Grading | Case, punctuation and spacing never matter; typed answers forgive one slip or a missing accent | `backend/app/services/grading.py` |
| Chest | 20 gems, once | `backend/app/services/rules.py` |
| Hearts | 5 at most; one comes back every 30 minutes (`HEART_REGEN_MINUTES`). In a lesson a wrong answer, wrong pair or SKIP costs one, and a lesson needs at least one to start | `backend/app/services/hearts.py`, `sessions.py` |
| Earning hearts back | Practice gives one back; a refill costs 350 gems | `backend/app/services/rules.py` |
| Streak | The day's first finished lesson or practice adds a day (or starts again at 1 after a gap), in the learner's time zone; reads 0 after a missed day | `backend/app/services/streak.py` |
| Daily goal | 10, 20, 30 or 50 XP (shown as 5, 10, 15, 20 minutes) | `backend/app/models/learner.py` |
| Leaderboards | Open after 10 finished lessons | `frontend/src/components/app/right-rail.tsx` |
| Achievements | Wildfire: longest streak of 3, 7, 14 ... 365 days (10 levels). Sage: 100, 250, 500 ... 30,000 XP (10 levels). Scholar: 5, 10, 25, 50 lessons. Sharpshooter: 3, 10, 25, 50 lessons without a mistake. Practice sessions count as lessons. Levels are checked when a session finishes and are never lost | `backend/app/seed/data.py`, `backend/app/services/achievements.py` |
| New learner | Starts at the first node with 500 gems, 5 hearts, no XP and no streak | `backend/app/services/learner.py` |

### Demo data

The seeded learner starts partway through Unit 1, so every node state is visible straight away: "Say hello"
finished, "Introduce yourself" at lesson 2 of 2, and the rest locked. Behind that are 3 real lessons on the 3
days before the database was first seeded: sessions, XP events, 30 XP and a 3-day streak that today's first lesson
extends. Those lessons have already earned level 1 of Wildfire (3-day streak) and Sharpshooter (3 lessons
without a mistake); two more sessions, practice included, unlock Scholar. This is the learner that "I already
have an account" opens. Finishing "Get started" replaces them
with a brand-new learner at the first node; `python -m app.seed --reset` restores this starting point.

The seed only ever adds what is missing, so it never rewrites content a database already has. After the course
content changes (the lesson player step trimmed each lesson node to 2 lessons), reset an existing database with
`python -m app.seed --reset`.

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
| POST | `/api/v1/me/hearts/refill` | Refill hearts for 350 gems |
| GET | `/api/v1/me/achievements` | Every achievement with the learner's level and progress towards the next |
| GET | `/api/v1/me/xp-history` | XP per day for the last 7 days (`?days=` up to 31), for the profile chart |
| POST | `/api/v1/sessions` | Start the active node's next lesson, or practice a finished node |
| GET | `/api/v1/sessions/current` | The session in progress (the lesson page plays it) |
| GET | `/api/v1/sessions/{session_id}` | One session with its exercises, without solutions |
| POST | `/api/v1/sessions/{session_id}/answers` | Grade one answer; wrong answers cost a heart in lessons |
| POST | `/api/v1/sessions/{session_id}/complete` | Finish: XP, streak, path progress (or a heart, for practice), new achievement levels |
| POST | `/api/v1/sessions/{session_id}/quit` | Leave a session early |

Every request and response, with real examples and every error code, is documented in
[docs/API.md](docs/API.md). With the backend running, `/docs` serves the same reference interactively.
Errors always have the shape `{"error": {"code": "...", "message": "...", "details": ...}}`.

## Brand assets

The logo, flags, icons, illustrations and animations in `frontend/public/landing/`, `frontend/public/onboarding/`
and `frontend/public/app/` are Duolingo's own artwork (the white trophy and the path's check mark are
recoloured or drawn here). They are used here only to reproduce the look of duolingo.com for a non-commercial
assignment, and remain the property of Duolingo, Inc. This project is not affiliated with Duolingo. To rebrand,
replace those folders; no code changes are needed.

Animations play through lottie-web's "light" player, which renders SVG and never runs the scripts some animation
files can carry. Each one has a still SVG poster, shown while it loads and to visitors who prefer reduced motion.

Duolingo's typefaces are proprietary, so the app uses Signika and Fredoka from Google Fonts as stand-ins.
