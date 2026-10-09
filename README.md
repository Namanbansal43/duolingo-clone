# Duolingo Clone

A full-stack Duolingo-style learning app built for an SDE assignment.

| Part | Stack | Status |
| --- | --- | --- |
| `frontend/` | Next.js 16 (App Router, TypeScript), Tailwind CSS v4 | Landing page, "Get started" flow, log in, `/learn`, lessons, profile, leaderboard, quests, shop, settings, dark mode |
| `backend/` | Python 3.12+, FastAPI, SQLAlchemy 2, Alembic, SQLite | Full schema, seeded Spanish course and rivals; learner, path, lesson, achievement, league, settings and demo-tools API |

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

## Deployment

The frontend runs on **Vercel** and the backend on **Railway**, each deployed from this repository's `main`
branch on every push.

```
browser ──> Vercel (Next.js) ──/api/* rewrite──> Railway (FastAPI in Docker) ──> SQLite on a volume
```

**Backend on Railway** (`backend/Dockerfile`, `backend/railway.json`)

1. New project → Deploy from GitHub repo → this repository.
2. In the service's settings: Root Directory `backend`; Config file path `/backend/railway.json`; branch `main`.
3. Add a volume to the service, mounted at `/data`. The image keeps the database at `/data/app.db`
   (`DATABASE_URL`), so progress survives restarts and redeploys.
4. Networking → Generate Domain. Railway sets `PORT` and the server listens on it.

On first boot the API creates the schema and seeds the demo, so there is nothing else to run. Railway waits for
`GET /api/health` to answer before switching traffic to a new deploy. The server runs a single worker, as
SQLite allows one writer at a time.

**Frontend on Vercel**

1. Add New → Project → import this repository.
2. Root Directory `frontend` (Vercel detects Next.js).
3. Environment variable `API_URL` = the Railway domain, e.g. `https://duolingo-clone-production.up.railway.app`
   (no trailing slash). It is read at build time by the `/api` rewrite, so redeploy after changing it.

The browser only talks to the Vercel site; Vercel forwards `/api/...` to Railway, so no CORS setup is needed.

To run the production image locally:

```bash
docker build -t duolingo-backend backend
docker run -p 8000:8000 -v duolingo-data:/data duolingo-backend
```

## Pages

| Path | What it is |
| --- | --- |
| `/` | Landing page, matching duolingo.com section by section |
| `/welcome` | The "Get started" flow (below) |
| `/log-in` | "I already have an account": log in to the demo account (below) |
| `/learn` | The learning path, inside the app shell (below) |
| `/lesson` | The lesson being played, full screen (below) |
| `/profile` | The learner's profile: statistics, XP this week, achievements (below) |
| `/profile/achievements` | Every achievement with its progress ("View all") |
| `/leaderboard` | This week's league: 30 learners ranked by XP (below) |
| `/quests` | The daily quest: today's XP against the daily goal (below) |
| `/shop` | Spend gems on a heart refill (below) |
| `/settings/preferences` | Sound, animations, motivational messages, listening exercises, daily goal and dark mode (below) |
| `/settings/demo` | Demo tools: move the app's clock forward a day, empty the hearts, reset the demo (below) |

### "Get started" flow

Every "Get started" button on the landing page opens `/welcome`, three screens modelled on duolingo.com's
own onboarding and measured against it at 1280×800:

1. **"I want to learn..."**: every course from `GET /api/v1/courses`, with the real number of learners
   studying it. Only Spanish has content; the other courses show a "coming soon" message.
2. **"Hi there! I'm Duo!"**: Duo waves (Duolingo's own Lottie animation).
3. **"What's your daily learning goal?"**: 5, 10, 15 or 20 minutes a day. Duolingo stores these as 10, 20, 30
   and 50 XP, and so does this app. The choices are native radio buttons, so arrow keys and Enter work.

Nothing is saved until the last CONTINUE, which sends one `POST /api/v1/me/onboarding` with the course, the daily
goal and the browser's time zone (so streak days follow the learner's own midnight), then opens `/learn`. Like a
new visitor on duolingo.com, the browser becomes a **guest**: a learner of its own, separate from the demo
account, starting at the first node with no history and no profile yet. The demo account is not touched. As on
duolingo.com, a guest sees a "Create a profile to save your progress!" card in the right rail, and Profile shows
that prompt instead of a profile. CREATE A PROFILE is "coming soon"; SIGN IN opens `/log-in` (see [the logged-in
learner](#the-logged-in-learner)). Leagues need an account, so once a guest has finished the 10 lessons that open
leaderboards, the leaderboard says "You need to sign in to join the leaderboard" with SIGN IN instead of
entering them.

Duolingo's flow also asks how you heard about it, why you are learning, how much you already know, and for
notification permission. Those screens are left out: nothing in this app would use the answers.

### `/log-in`

"I already have an account" on the landing page, and SIGN IN anywhere a guest sees it, open duolingo.com's log-in
screen, measured against it at 1280×800: the close button, SIGN UP (to "Get started"), "Log in", the two fields
and LOG IN. The brief assumes one logged-in learner, so there is a single demo account (`alex`, filled in) and no
password; Duolingo's Google, Facebook and Apple buttons are left out. LOG IN (`POST /api/v1/me/sign-in`) makes
this browser the demo learner again and opens `/learn` with Alex's progress, which stays until "Reset the demo".

### `/learn`: the app shell and the learning path

Measured against duolingo.com's own `/learn` page (opened as a guest) at 1280, 1024, 800 and 390 px wide.

- **App shell**, shared by every signed-in page (`frontend/src/app/(app)/layout.tsx`): a left sidebar with
  Learn, Leaderboards, Quests, Shop, Profile and More. It is 256 px wide with labels from 1160 px, icons only
  below that, and becomes a bottom tab bar on phones. MORE opens a menu with Settings.
- **Right rail** (1024 px and up; a stats bar across the top below that): course flag, streak, gems and hearts
  from `GET /api/v1/me` (switching courses is "coming soon", as only Spanish has content); the league card
  (`GET /api/v1/leaderboard`): "Unlock Leaderboards!" counting down the 10 lessons that open them, then the
  league with "You're ranked #12" and VIEW LEAGUE; and the daily quest, which tracks today's XP against the daily
  goal (VIEW ALL opens `/quests`).
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
  streak screen with the flame, the new count and the days around today, then "You unlocked Leaderboards!" after
  the 10th lesson, then "Achievement unlocked!" for each achievement that went up a level, with its badge and
  what the next level needs.
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
- **Statistics**: day streak, total XP, current league (with its badge; "None" until leaderboards open) and top
  3 finishes, the last two from `GET /api/v1/leaderboard`.
- **XP this week**: a line chart of the last 7 days from `GET /api/v1/me/xp-history`, drawn as plain SVG at
  duolingo.com's proportions, with the week's total.
- **Achievements**: a row of badges in Duolingo's artwork, coloured once reached and gold at the top level;
  "View all" opens `/profile/achievements`, which lists each one with its level, a progress bar ("3/7") and the
  next goal. Both read `GET /api/v1/me/achievements`.
- **Right rail**: the stats bar and a Following / Followers card with Duolingo's empty states.
- **Guests**: after "Get started" there is no profile yet, so `/profile` and "View all" show "Create a profile to
  save your progress!" with CREATE A PROFILE ("coming soon") and SIGN IN instead.

**Where XP shows.** The brief lists XP in the top bar, but duolingo.com's top bar has only the flag, streak, gems
and hearts. To keep that bar identical, total XP is on the profile, today's XP is in the Daily Quests card on
`/learn`, and each lesson's XP is on its result screen.

### `/leaderboard`: weekly leagues

Measured against duolingo.com's leaderboard page (opened as a guest), with the wording of its active league
taken from duolingo.com's own interface strings ("Top 7 advance to the next league", "Promotion zone", "You
finished #3 and advanced to the Silver League"...).

- **Header**: the ten league badges in a row, centred on the learner's league (leagues passed in colour, the
  ones above locked), the league's name, "Top 7 advance to the next league" and the time left in the week.
- **Standings**: the learner and 29 seeded rivals, by XP this week. Ranks 1 to 3 get medals; ranks in the
  promotion zone are green and those in the demotion zone red, with a "Promotion zone" / "Demotion zone" line
  between them. The learner's row is highlighted. Avatars are initials on a colour, like a Duolingo learner
  without a picture.
- **Before joining**: with leaderboards locked the page says "Unlock Leaderboards! Complete 10 more lessons to
  start competing"; once open, each week starts with "Complete a lesson to join this week's leaderboard". Both
  show Duolingo's grey placeholder list and START A LESSON, and the learner's own empty row at the bottom.
- **Guests**: a guest from "Get started" counts down the same 10 lessons, then sees "You need to sign in to join
  the leaderboard" with SIGN IN (to `/log-in`), and the rail card says "Sign in to start competing". Guests never
  join a league.
- **A new week**: the first visit after a week ends shows how it went ("You finished #3 and advanced to the
  Silver League", "...kept your position in...", "...dropped down to..."), once.
- **Live rivals**: the rivals keep practising through the week (see the rules below), so ranks change between
  visits even without playing.

### `/quests` and `/shop`

Both are measured against duolingo.com's own pages and kept to what the brief asks for: a daily goal
indicator, and hearts refilled with mocked gems. Neither needs new API endpoints.

- **Quests** shows the brief's daily goal as Duolingo's daily quest: "Earn 20 XP", filled by today's XP
  (`xp_today` from `GET /api/v1/me`), with the time left until it refreshes at midnight in the learner's time
  zone. As on duolingo.com for a new learner, the page opens with the purple "Welcome!" banner, the next card
  reads "More quests unlock soon", and the rail says "Monthly challenges unlock soon!" with START A LESSON.
  Quest rewards are not part of the brief, so finishing the quest only fills the bar.
- **Shop** has duolingo.com's Hearts section: Refill Hearts for 350 gems (`POST /api/v1/me/hearts/refill`,
  the same purchase the out-of-hearts screen offers). The button reads FULL when hearts are full and is greyed
  out without enough gems. Gems are mocked, as the brief allows: they come from the starting 500 and treasure
  chests, never from money. As on duolingo.com, a guest sees "You earned 500 gems! Create a profile to spend
  them in the store!" over the shop. Duolingo's Power-Ups section (Streak Freeze) is left out: it isn't in
  the brief.

### `/settings`: preferences, dark mode and demo tools

Settings open from the sidebar's MORE menu (on phones, from the gear on the profile), as on duolingo.com.
The Preferences page is measured against duolingo.com's own, opened as a guest.

- **Lesson experience**: Duolingo's four switches, and each one does something here.
  - *Sound effects*: the right, wrong and lesson-complete sounds.
  - *Animations*: off stops motion across the app (celebrations, the bobbing START, animated illustrations).
  - *Motivational messages*: the "5 in a row" streak inside a lesson.
  - *Listening exercises*: off leaves them out of lessons, just as "Can't listen now" does mid-lesson.
- **Daily goal**: the goal chosen in "Get started" (Casual, Regular, Serious, Intense), changeable here.
- **Appearance**: Dark mode, *System default* (follows the device), *On* or *Off*. Dark mode uses
  duolingo.com's own dark palette, read from its page: the page turns `#131F24`, cards `#202F36`, borders
  `#37464F`, text near-white, and coloured buttons get dark text. It covers the app and the lesson; the landing
  page and "Get started" stay light, as Duolingo's do.
- **The menu**: Duolingo's settings sections, grouped as on its site (Account, Subscription, Support). Profile,
  Notifications, Courses, Privacy settings, Choose a plan, Help Center and Feedback are the "settings
  placeholders" the brief allows and say "coming soon". A guest sees Duolingo's shorter guest menu.
- **Demo tools** (this clone's own section, not Duolingo's): with one built-in learner, and a day taking a real
  day, these let a reviewer try what depends on time.
  - *Advance a day* moves the app's clock forward 24 hours. Everything follows it: a lesson the next day
    extends the streak and a day without one breaks it, hearts regenerate, rivals keep earning XP, and moving
    past Sunday ends the league week with its promotion or demotion.
  - *Empty hearts* takes every heart away, to see the out-of-hearts screen.
  - *Reset the demo* puts everything back as first seeded (the demo learner, their history, the rivals and
    real time), removes the guest from "Get started", and keeps the preferences. The browser is the demo
    learner afterwards.

Every change saves at once, as on Duolingo. The settings live on the server (`user_settings`); the browser only
remembers the last dark mode choice so the next page load paints in the right theme before they arrive.

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
| Earning hearts back | Practice gives one back; a refill costs 350 gems (shop or out-of-hearts screen) | `backend/app/services/rules.py` |
| Streak | The day's first finished lesson or practice adds a day (or starts again at 1 after a gap), in the learner's time zone; reads 0 after a missed day | `backend/app/services/streak.py` |
| Daily goal | 10, 20, 30 or 50 XP (shown as 5, 10, 15, 20 minutes); it is the daily quest, which resets at midnight in the learner's time zone | `backend/app/models/learner.py` |
| Leaderboards | Open after 10 finished lessons (practice included); then each week, finishing a lesson joins that week's league. A guest is asked to sign in instead | `backend/app/services/rules.py`, `leagues.py` |
| Leagues | Bronze, Silver, Gold, Sapphire, Ruby, Emerald, Amethyst, Pearl, Obsidian, Diamond. A week runs Monday to Sunday in the learner's time zone; 30 learners compete by XP earned that week. The top 7 move up a league and the bottom 5 down (none down from Bronze, none up from Diamond) | `backend/app/seed/data.py`, `backend/app/services/leagues.py` |
| Rivals | 29 seeded learners, from keen to occasional. They follow the learner from league to league. Each rival's day (whether they practise, when, and how much XP) is fixed by their id and the date, and is written as real XP events whenever the leaderboard is read, so no background job runs | `backend/app/services/leagues.py` |
| Achievements | Wildfire: longest streak of 3, 7, 14 ... 365 days (10 levels). Sage: 100, 250, 500 ... 30,000 XP (10 levels). Scholar: 5, 10, 25, 50 lessons. Sharpshooter: 3, 10, 25, 50 lessons without a mistake. Practice sessions count as lessons. Levels are checked when a session finishes and are never lost | `backend/app/seed/data.py`, `backend/app/services/achievements.py` |
| New learner ("Get started") | A guest of its own, separate from the demo account: starts at the first node with 500 gems, 5 hearts, no XP and no streak, without a profile; the current preferences carry over | `backend/app/services/learner.py` |
| The app's clock | Real time plus the days advanced with the demo tools (`demo_clock`). Every request reads time from it, and `/me` returns it as `now` so the page's countdowns agree | `backend/app/services/demo.py`, `frontend/src/lib/clock.ts` |

### Demo data

The seeded learner starts partway through Unit 1, so every node state is visible straight away: "Say hello"
finished, "Introduce yourself" at lesson 2 of 2, and the rest locked. Behind that are 3 real lessons on the 3
days before the database was first seeded: sessions, XP events, 30 XP and a 3-day streak that today's first lesson
extends. Those lessons have already earned level 1 of Wildfire (3-day streak) and Sharpshooter (3 lessons
without a mistake); two more sessions, practice included, unlock Scholar. Leaderboards normally open after 10
lessons, but this learner is already in this week's Bronze League with the 29 rivals, whose XP runs from the
Monday of the week the database was seeded. This is the account "I already have an account" logs in to.
"Get started" never touches it: the guest is a separate learner. "Reset the demo" in Settings (or
`python -m app.seed --reset`) restores this starting point.

The seed only ever adds what is missing, so it never rewrites content a database already has. After the course
content changes (the lesson player step trimmed each lesson node to 2 lessons), reset an existing database with
`python -m app.seed --reset`.

## Database

20 tables covering course content, learner progress and preferences, lesson history, XP, achievements, leagues
and the demo clock. The ER diagram,
the rules the database enforces and the design decisions are in [docs/DATABASE.md](docs/DATABASE.md).

## The logged-in learner

The brief asks us to assume a logged-in user, so there is no real sign-up or password. The seed creates the
demo account (`alex`), and an API request acts as them unless the browser went through "Get started":

| The browser... | Acts as | How |
| --- | --- | --- |
| Opened the app directly, or logged in ("I already have an account", SIGN IN) | The demo learner, `alex` | No `learner` cookie (`POST /api/v1/me/sign-in` clears it) |
| Finished "Get started" | The guest (`users.is_guest`), a separate learner | `POST /api/v1/me/onboarding` sets an HttpOnly cookie, `learner=guest` |

The `get_current_user` dependency in `backend/app/deps.py` is the only code that reads the cookie and decides who
"me" is; adding real authentication would mean replacing that one function. Keeping the guest apart means trying
"Get started" never wipes the demo account, in this tab or any other. The guest's own progress stays with the
guest until the next "Get started" starts it over; it is not merged into the demo account on logging in, just as
logging in to an existing account on duolingo.com doesn't merge a guest's progress. The settings-page
preferences carry over both ways, as they describe the device rather than the progress.

The browser cookie goes through the frontend's `/api` proxy, so it is a first-party cookie of the site. There is
one demo account and one guest, so on a shared deployment everyone who logs in shares Alex's progress, and two
visitors in "Get started" at the same time share the guest.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Liveness check, including the database |
| GET | `/api/v1/me` | The learner with live stats: hearts after regeneration, streak and XP as of today |
| PATCH | `/api/v1/me` | Set the active course, daily goal (10/20/30/50 XP) or time zone, keeping progress |
| POST | `/api/v1/me/onboarding` | Finish "Get started": the browser becomes a new guest with the chosen course, goal and time zone |
| POST | `/api/v1/me/sign-in` | "I already have an account": the browser is the demo learner again |
| GET | `/api/v1/courses` | All courses in display order with learner counts; only Spanish is available |
| GET | `/api/v1/courses/{course_id}/path` | The course's units and nodes, each completed, active or locked |
| POST | `/api/v1/skills/{skill_id}/open-chest` | Open the treasure chest the learner has reached (+20 gems) |
| POST | `/api/v1/me/hearts/refill` | Refill hearts for 350 gems |
| GET | `/api/v1/me/achievements` | Every achievement with the learner's level and progress towards the next |
| GET | `/api/v1/me/xp-history` | XP per day for the last 7 days (`?days=` up to 31), for the profile chart |
| GET | `/api/v1/me/settings` | The learner's preferences: the four lesson switches and dark mode |
| PATCH | `/api/v1/me/settings` | Change some of them |
| GET | `/api/v1/leaderboard` | This week's league: standings, zones, time left, last week's result |
| POST | `/api/v1/sessions` | Start the active node's next lesson, or practice a finished node |
| GET | `/api/v1/sessions/current` | The session in progress (the lesson page plays it) |
| GET | `/api/v1/sessions/{session_id}` | One session with its exercises, without solutions |
| POST | `/api/v1/sessions/{session_id}/answers` | Grade one answer; wrong answers cost a heart in lessons |
| POST | `/api/v1/sessions/{session_id}/complete` | Finish: XP, streak, path progress (or a heart, for practice), new achievement levels, this week's league |
| POST | `/api/v1/sessions/{session_id}/quit` | Leave a session early |
| GET | `/api/v1/demo/clock` | How many days the app's clock runs ahead, and its time now |
| POST | `/api/v1/demo/clock/advance` | Move the app's clock forward a day |
| POST | `/api/v1/demo/hearts/empty` | Lose every heart, to try the out-of-hearts screen |
| POST | `/api/v1/demo/reset` | Everything back to the seeded state and real time, the guest removed; preferences kept |

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
