# API reference

The backend is a FastAPI app. Every endpoint, request and response is listed below; every example is a real
response from the API, captured on a freshly seeded database with the clock fixed at `2026-10-08T12:00:00Z`.
The seed gives the built-in learner a few days of history (3 lessons finished on the 3 days before), so the
examples show a learner partway through Unit 1.

| | |
| --- | --- |
| Base URL (local) | `http://localhost:8000` |
| Interactive docs | `/docs` (Swagger UI, lets you send requests), `/redoc`, raw schema at `/openapi.json` |
| Versioning | Application endpoints live under `/api/v1`; the health check is unversioned at `/api/health` |

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | [`/api/health`](#get-apihealth) | Liveness check, including the database |
| GET | [`/api/v1/me`](#get-apiv1me) | The logged-in learner with live stats |
| PATCH | [`/api/v1/me`](#patch-apiv1me) | Change the learner's course, daily goal or time zone |
| POST | [`/api/v1/me/onboarding`](#post-apiv1meonboarding) | Finish "Get started": the learner starts over |
| GET | [`/api/v1/courses`](#get-apiv1courses) | The course catalogue |
| GET | [`/api/v1/courses/{course_id}/path`](#get-apiv1coursescourse_idpath) | A course's learning path with the learner's progress |
| POST | [`/api/v1/skills/{skill_id}/open-chest`](#post-apiv1skillsskill_idopen-chest) | Open a treasure chest on the path |
| POST | [`/api/v1/me/hearts/refill`](#post-apiv1meheartsrefill) | Refill hearts for 350 gems |
| POST | [`/api/v1/sessions`](#post-apiv1sessions) | Start a lesson, or practice a finished node |
| GET | [`/api/v1/sessions/current`](#get-apiv1sessionscurrent) | The session in progress |
| GET | [`/api/v1/sessions/{session_id}`](#get-apiv1sessionssession_id) | One session |
| POST | [`/api/v1/sessions/{session_id}/answers`](#post-apiv1sessionssession_idanswers) | Answer one exercise; graded on the server |
| POST | [`/api/v1/sessions/{session_id}/complete`](#post-apiv1sessionssession_idcomplete) | Finish the session: XP, streak, path progress |
| POST | [`/api/v1/sessions/{session_id}/quit`](#post-apiv1sessionssession_idquit) | Leave a session early |

## Conventions

- **No authentication.** The brief assumes a logged-in user, so every request acts as the built-in learner
  (`alex`). No token or cookie is needed. Real auth would only replace `get_current_user` in
  `backend/app/deps.py`.
- **JSON in, JSON out.** Send `Content-Type: application/json` with request bodies.
- **Times** are ISO 8601 in UTC with a `Z` suffix, e.g. `2026-10-08T12:20:00Z`. IDs are integers.
- **PATCH is partial.** Fields you leave out, or send as `null`, are not changed. Unknown or read-only fields are
  rejected with `422`, so a typo never fails silently.
- **CORS.** Browsers may call the API from the origins in `CORS_ORIGINS` (default `http://localhost:3000`).

## Errors

Every error response, from any endpoint, has the same body:

```json
{
  "error": {
    "code": "course_unavailable",
    "message": "French is coming soon."
  }
}
```

| Field | Type | Description |
| --- | --- | --- |
| `error.code` | string | Stable, machine-readable. Clients should branch on this, not on `message`. |
| `error.message` | string | Human-readable explanation. |
| `error.details` | array | Only for `validation_error`: one entry per problem (see below). Absent otherwise. |

All error codes the API returns today:

| Status | `code` | When | Returned by |
| --- | --- | --- | --- |
| 404 | `not_found` | The path doesn't exist | Any URL |
| 404 | `course_not_found` | No course has that id | `PATCH /api/v1/me`, `POST .../me/onboarding`, `GET .../courses/{id}/path` |
| 404 | `skill_not_found` | No path node has that id | `POST .../skills/{id}/open-chest`, `POST /api/v1/sessions` |
| 404 | `session_not_found` | No session of this learner has that id, or (for `current`) none is in progress | `/api/v1/sessions/...` |
| 404 | `exercise_not_found` | The exercise isn't part of the session | `POST .../sessions/{id}/answers` |
| 405 | `method_not_allowed` | The path exists but not with this method | Any URL |
| 409 | `course_unavailable` | The course exists but is "coming soon" | `PATCH /api/v1/me`, `POST .../me/onboarding`, `GET .../courses/{id}/path` |
| 409 | `not_a_chest` | The path node isn't a treasure chest | `POST .../skills/{id}/open-chest` |
| 409 | `skill_locked` | The node hasn't been reached yet | `POST .../skills/{id}/open-chest`, `POST /api/v1/sessions` |
| 409 | `not_a_lesson` | The node is a treasure chest: it is opened, not played | `POST /api/v1/sessions` |
| 409 | `lesson_unavailable` | The lesson has no exercises yet (Units 2 and 3) | `POST /api/v1/sessions` |
| 409 | `out_of_hearts` | No hearts left, and a lesson needs one | `POST /api/v1/sessions`, `POST .../answers` |
| 409 | `session_finished` | The session already ended | `POST .../answers`, `.../complete`, `.../quit` |
| 409 | `exercise_completed` | That exercise was already answered correctly | `POST .../answers` |
| 409 | `session_incomplete` | Exercises are left to answer | `POST .../complete` |
| 409 | `hearts_full` | Hearts are already full | `POST /api/v1/me/hearts/refill` |
| 409 | `not_enough_gems` | Fewer than 350 gems | `POST /api/v1/me/hearts/refill` |
| 409 | `chest_already_opened` | The chest was opened before | `POST .../skills/{id}/open-chest` |
| 422 | `validation_error` | The body is not valid JSON, misses a required field, has an invalid value or an unknown field, or an id in the URL isn't a whole number | Every endpoint with a body or an id in the URL |
| 422 | `invalid_answer` | The answer uses the wrong field for the exercise type, or options that aren't the exercise's | `POST .../sessions/{id}/answers` |
| 500 | `internal_error` | An unexpected server error (the details are logged on the server, never sent) | Any endpoint |
| 503 | `learner_missing` | The database has not been seeded with the built-in learner | Every endpoint that acts as the learner |

Each entry in `details` describes one problem:

| Field | Description |
| --- | --- |
| `type` | Kind of problem, e.g. `literal_error`, `extra_forbidden`, `json_invalid`, `value_error`, `int_parsing`, `missing` |
| `loc` | Where it is: `["body", "<field>"]`, or `["path", "<parameter>"]` for an id in the URL |
| `msg` | What is wrong |
| `input` | The value that was sent |
| `ctx` | Extra context for some types, e.g. the allowed values |

## Shared objects

### Course

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer | Course id; pass it as `active_course_id` to switch course |
| `learning_language` | string | Code of the language being learned, e.g. `es`. Also names its flag image. |
| `from_language` | string | Code of the language the course is taught in, e.g. `en` |
| `title` | string | Display name, e.g. `Spanish` |
| `is_available` | boolean | `false` means the course is shown as "coming soon" and can't be selected |

### Catalogue course

A [Course](#course) with one extra field, returned by `GET /api/v1/courses`.

| Field | Type | Description |
| --- | --- | --- |
| `learners` | integer | Learners whose active course this is. Shown on the course picker ("1 learner"). |

### Me

The learner, with stats as they are right now.

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer | Learner id |
| `username` | string | Unique handle, e.g. `alex` |
| `display_name` | string | Name shown in the app |
| `joined_at` | datetime | When the learner signed up: when the database was seeded, or when they last finished "Get started" |
| `timezone` | string | IANA time zone, e.g. `Asia/Kolkata`. Decides when the learner's day starts. |
| `active_course` | [Course](#course) or null | The course being studied |
| `daily_goal_xp` | integer | XP per day: `10` Casual, `20` Regular, `30` Serious, `50` Intense |
| `total_xp` | integer | All XP ever earned |
| `xp_today` | integer | XP earned today, in the learner's time zone. Compare with `daily_goal_xp` for the daily goal. |
| `lessons_completed` | integer | Lessons finished so far (leaderboards open after 10) |
| `gems` | integer | Gem balance |
| `hearts` | [Hearts](#hearts) | Hearts right now |
| `streak` | [Streak](#streak) | Streak as of today |

### Hearts

| Field | Type | Description |
| --- | --- | --- |
| `current` | integer | Hearts right now, including any that regenerated since hearts were last spent |
| `max` | integer | Most hearts the learner can hold |
| `next_heart_at` | datetime or null | When the next heart comes back; `null` when hearts are full |
| `regen_minutes` | integer | Minutes to regenerate one heart (30 in this demo; set by `HEART_REGEN_MINUTES`) |

Hearts are not topped up by a background job. The server stores the count at the moment hearts were last spent
and works out the live count from the time elapsed. For example, 3 hearts stored at 11:20 read as 4 hearts at
12:00 (one 30-minute interval has passed), with the next heart due at 12:20.

### Streak

| Field | Type | Description |
| --- | --- | --- |
| `length` | integer | Current streak in days. Reads `0` once a full day is missed. |
| `extended_today` | boolean | Whether today already counts, in the learner's time zone |
| `longest` | integer | Longest streak ever reached |

### Path

| Field | Type | Description |
| --- | --- | --- |
| `course` | [Course](#course) | The course this path belongs to |
| `units` | [Path unit](#path-unit)[] | In order |
| `active_node_id` | integer or null | The node to play next; `null` once every node is completed |

### Path unit

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer | Unit id |
| `position` | integer | Unit number in the course, from 1 ("Unit 1") |
| `title` | string | e.g. "Greet people and introduce yourself" |
| `nodes` | [Path node](#path-node)[] | In path order |

### Path node

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer | Node (skill) id |
| `position` | integer | Order within the unit, from 1 |
| `title` | string | e.g. "Say hello" |
| `kind` | string | `lesson` (star), `chest` (treasure chest) or `review` (the trophy that ends a unit) |
| `state` | string | `completed`, `active` (play this next) or `locked` |
| `lessons_total` | integer | Lessons in the node; `0` for a chest |
| `lessons_completed` | integer | Lessons finished so far; drives the progress ring around the active node |

Nodes unlock strictly in order: everything before the first unfinished node is `completed`, that node is
`active`, and everything after it is `locked`, across unit boundaries too. Only completion is stored; the states
are worked out on every request, so they can never contradict each other.

### Session

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer | Session id |
| `mode` | string | `lesson` (the active node's next lesson) or `practice` (a finished node: no hearts lost) |
| `status` | string | `in_progress`, `completed`, `failed` (quit with no hearts left) or `abandoned` |
| `started_at` | datetime | When it started |
| `node` | object | The path node: `{"id", "title"}` |
| `lesson_position` | integer | Which lesson of the node this is, from 1 |
| `lessons_total` | integer | Lessons in the node |
| `exercises` | [Exercise](#exercise)[] | In order |
| `completed_exercise_ids` | integer[] | Exercises already answered correctly, so a reload can carry on |
| `hearts` | [Hearts](#hearts) | The learner's hearts right now |

### Exercise

Sent without its solution: which option is right, and the accepted answers, stay on the server.

| Field | Type | Description |
| --- | --- | --- |
| `id` | integer | Exercise id |
| `type` | string | `multiple_choice`, `word_bank`, `match_pairs`, `fill_blank`, `type_answer` or `listen` |
| `instruction` | string | The heading, e.g. "Write this in English" |
| `prompt` | string or null | The word or sentence to work on; contains `___` for `fill_blank`; null for `match_pairs`. For `listen` it is the sentence read aloud (the browser's text-to-speech needs the text) |
| `prompt_language` | string or null | `es` or `en` |
| `options` | object[] | `{"id", "text"}`: the choices (`multiple_choice`, `fill_blank`) or word tiles (`word_bank`, `listen`), shuffled. Empty otherwise |
| `pairs` | object or null | `match_pairs` only: `{"left": [English], "right": [Spanish]}`, each shuffled |

Shuffled lists keep the same order for the whole session, so a reload doesn't move them.

### Answer result

| Field | Type | Description |
| --- | --- | --- |
| `correct` | boolean | Whether the answer counts |
| `verdict` | string | `correct`; `other_solution` (right, but the main translation differs); `typo` (right apart from one slip or a missing accent); `wrong` |
| `solution` | string or null | What the feedback bar shows under its heading: the correct solution (`wrong`), the main translation (`other_solution`) or the right spelling (`typo`) |
| `exercise_completed` | boolean | False only for `match_pairs` while pairs are left |
| `hearts` | [Hearts](#hearts) | After this answer |

### Completion

| Field | Type | Description |
| --- | --- | --- |
| `xp_earned` | integer | 10 for a lesson, 5 for practice |
| `total_xp`, `xp_today`, `daily_goal_xp` | integer | Totals after this session, for the daily goal |
| `accuracy` | integer | Percent of exercises answered right the first time |
| `duration_seconds` | integer | From start to finish |
| `streak` | object | `{"length", "longest", "extended"}`; `extended` is true when this was today's first finished session |
| `hearts` | [Hearts](#hearts) | After this session (practice gives one back) |
| `node` | object | `{"id", "lessons_completed", "lessons_total", "completed"}`: the path node's progress |

---

## GET /api/health

Liveness check. Answers only if the API can reach the database, so hosting platforms can use it as a health
probe.

**Request:** no parameters, no body.

**Response `200 OK`**

| Field | Type | Description |
| --- | --- | --- |
| `status` | string | Always `"ok"` |

```json
{
  "status": "ok"
}
```

**Errors:** `500 internal_error` if the database can't be reached.

```bash
curl http://localhost:8000/api/health
```

---

## GET /api/v1/me

The logged-in learner with live stats. The frontend calls this for the top bar (streak, gems, hearts), the
daily goal and the profile.

**Request:** no parameters, no body.

**Response `200 OK`:** a [Me](#me) object.

```json
{
  "id": 1,
  "username": "alex",
  "display_name": "Alex",
  "joined_at": "2026-10-05T12:00:00Z",
  "timezone": "UTC",
  "active_course": {
    "id": 1,
    "learning_language": "es",
    "from_language": "en",
    "title": "Spanish",
    "is_available": true
  },
  "daily_goal_xp": 20,
  "total_xp": 30,
  "xp_today": 0,
  "lessons_completed": 3,
  "gems": 500,
  "hearts": {
    "current": 5,
    "max": 5,
    "next_heart_at": null,
    "regen_minutes": 30
  },
  "streak": {
    "length": 3,
    "extended_today": false,
    "longest": 3
  }
}
```

The streak reads `extended_today: false` because the seeded history ends yesterday: finishing a lesson today
extends it. While hearts are not full, `hearts` looks like
`{"current": 4, "max": 5, "next_heart_at": "2026-10-08T12:20:00Z", "regen_minutes": 30}`.

**Errors**

| Status | `code` | Example |
| --- | --- | --- |
| 503 | `learner_missing` | `{"error": {"code": "learner_missing", "message": "The default learner has not been seeded yet."}}` |
| 500 | `internal_error` | `{"error": {"code": "internal_error", "message": "Something went wrong on our side."}}` |

```bash
curl http://localhost:8000/api/v1/me
```

---

## PATCH /api/v1/me

Changes the learner's own preferences and keeps their progress; the settings page will use it. Send only the
fields you want to change. (The "Get started" flow uses [`POST /api/v1/me/onboarding`](#post-apiv1meonboarding)
instead, which starts the learner over.)

**Request body**

| Field | Type | Rules |
| --- | --- | --- |
| `active_course_id` | integer | Must be the `id` of a course with `is_available: true` |
| `daily_goal_xp` | integer | One of `10`, `20`, `30`, `50` |
| `timezone` | string | A valid IANA time zone name, at most 64 characters, e.g. `Asia/Kolkata` |

Any other field, including stats such as `gems` or `hearts`, is rejected. An empty body `{}` changes nothing
and returns the learner unchanged.

```json
{
  "daily_goal_xp": 30,
  "timezone": "Asia/Kolkata"
}
```

**Response `200 OK`:** the updated [Me](#me) object, so the client doesn't need a second request.

```json
{
  "id": 1,
  "username": "alex",
  "display_name": "Alex",
  "joined_at": "2026-10-05T12:00:00Z",
  "timezone": "Asia/Kolkata",
  "active_course": {
    "id": 1,
    "learning_language": "es",
    "from_language": "en",
    "title": "Spanish",
    "is_available": true
  },
  "daily_goal_xp": 30,
  "total_xp": 30,
  "xp_today": 0,
  "lessons_completed": 3,
  "gems": 500,
  "hearts": {
    "current": 5,
    "max": 5,
    "next_heart_at": null,
    "regen_minutes": 30
  },
  "streak": {
    "length": 3,
    "extended_today": false,
    "longest": 3
  }
}
```

**Errors**

| Status | `code` | Cause |
| --- | --- | --- |
| 404 | `course_not_found` | `active_course_id` doesn't match any course |
| 409 | `course_unavailable` | The course exists but is coming soon |
| 422 | `validation_error` | Daily goal not an allowed value, unknown time zone, unknown field, or malformed JSON |
| 503 | `learner_missing` | The database has not been seeded |
| 500 | `internal_error` | Unexpected server error |

`404`, for `{"active_course_id": 9999}`:

```json
{
  "error": {
    "code": "course_not_found",
    "message": "That course does not exist."
  }
}
```

`409`, for `{"active_course_id": 2}` (French):

```json
{
  "error": {
    "code": "course_unavailable",
    "message": "French is coming soon."
  }
}
```

`422`, for `{"daily_goal_xp": 25}`:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request is invalid.",
    "details": [
      {
        "type": "literal_error",
        "loc": ["body", "daily_goal_xp"],
        "msg": "Input should be 10, 20, 30 or 50",
        "input": 25,
        "ctx": { "expected": "10, 20, 30 or 50" }
      }
    ]
  }
}
```

The other `422` cases differ only in their `details` entry:

| Request body | `details[0].type` | `details[0].loc` | `details[0].msg` |
| --- | --- | --- | --- |
| `{"timezone": "Mars/Olympus_Mons"}` | `value_error` | `["body", "timezone"]` | `Value error, unknown IANA time zone` |
| `{"gems": 99999}` | `extra_forbidden` | `["body", "gems"]` | `Extra inputs are not permitted` |
| `{not json` | `json_invalid` | `["body", 1]` | `JSON decode error` |

```bash
curl -X PATCH http://localhost:8000/api/v1/me \
  -H "Content-Type: application/json" \
  -d '{"daily_goal_xp": 30, "timezone": "Asia/Kolkata"}'
```

---

## POST /api/v1/me/onboarding

Finishes the "Get started" flow. Signing up means a new account, so the learner starts over and their path begins
again at its first node. The brief has a single built-in learner, so this resets that learner:

| What | Becomes |
| --- | --- |
| Lesson sessions and their answers, XP events, path progress, unlocked achievements | Deleted |
| `total_xp`, the streak (current and longest), streak freezes | 0 |
| Hearts | Full |
| Gems | 500, a new learner's balance |
| `joined_at` | Now |
| Course, daily goal, time zone | The values sent |

The username, display name and settings-page preferences are kept. If the request is refused (any error below),
nothing changes. "I already have an account" doesn't call this: it opens `/learn` with the learner as they are.

**Request body:** all three fields are required.

| Field | Type | Rules |
| --- | --- | --- |
| `active_course_id` | integer | Must be the `id` of a course with `is_available: true` |
| `daily_goal_xp` | integer | One of `10`, `20`, `30`, `50` |
| `timezone` | string | A valid IANA time zone name, at most 64 characters. The frontend sends the browser's own. |

```json
{
  "active_course_id": 1,
  "daily_goal_xp": 30,
  "timezone": "Asia/Kolkata"
}
```

**Response `200 OK`:** the new learner, as a [Me](#me) object. Their path
([`GET /api/v1/courses/1/path`](#get-apiv1coursescourse_idpath)) now has its first node `active` and every other
node `locked`, with `active_node_id` pointing at the first node.

```json
{
  "id": 1,
  "username": "alex",
  "display_name": "Alex",
  "joined_at": "2026-10-08T12:00:00Z",
  "timezone": "Asia/Kolkata",
  "active_course": {
    "id": 1,
    "learning_language": "es",
    "from_language": "en",
    "title": "Spanish",
    "is_available": true
  },
  "daily_goal_xp": 30,
  "total_xp": 0,
  "xp_today": 0,
  "lessons_completed": 0,
  "gems": 500,
  "hearts": {
    "current": 5,
    "max": 5,
    "next_heart_at": null,
    "regen_minutes": 30
  },
  "streak": {
    "length": 0,
    "extended_today": false,
    "longest": 0
  }
}
```

**Errors**

| Status | `code` | Cause |
| --- | --- | --- |
| 404 | `course_not_found` | `active_course_id` doesn't match any course |
| 409 | `course_unavailable` | The course exists but is coming soon |
| 422 | `validation_error` | A field is missing, the daily goal isn't an allowed value, unknown time zone, unknown field, or malformed JSON |
| 503 | `learner_missing` | The database has not been seeded |
| 500 | `internal_error` | Unexpected server error |

The `404`, `409` and most `422` bodies are the same as for [`PATCH /api/v1/me`](#patch-apiv1me). A missing field
looks like this, for a body without `daily_goal_xp`:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request is invalid.",
    "details": [
      {
        "type": "missing",
        "loc": ["body", "daily_goal_xp"],
        "msg": "Field required",
        "input": { "active_course_id": 1, "timezone": "Asia/Kolkata" }
      }
    ]
  }
}
```

```bash
curl -X POST http://localhost:8000/api/v1/me/onboarding \
  -H "Content-Type: application/json" \
  -d '{"active_course_id": 1, "daily_goal_xp": 30, "timezone": "Asia/Kolkata"}'
```

---

## POST /api/v1/me/hearts/refill

Refills hearts to full for 350 gems. Purchases are mocked: gems come from chests and the starting balance,
never from money. The out-of-hearts screen offers this.

**Request:** no body.

**Response `200 OK`:** the learner as a [Me](#me) object, with full hearts and 350 gems fewer (here 500 → 150).

**Errors**

| Status | `code` | Cause |
| --- | --- | --- |
| 409 | `hearts_full` | `{"error": {"code": "hearts_full", "message": "Your hearts are already full."}}` |
| 409 | `not_enough_gems` | The learner has fewer than 350 gems |
| 503 | `learner_missing` | The database has not been seeded |

```bash
curl -X POST http://localhost:8000/api/v1/me/hearts/refill
```

---

## GET /api/v1/courses

Every course in display order, the same order as the course strip on the landing page, with how many learners
study each one. Only Spanish has content; the other 38 are returned with `is_available: false` so the UI can show
them as "coming soon". Used by the course picker of the "Get started" flow.

**Request:** no parameters, no body.

**Response `200 OK`:** an array of [Catalogue course](#catalogue-course) objects (39 today). The first three:

```json
[
  {
    "id": 1,
    "learning_language": "es",
    "from_language": "en",
    "title": "Spanish",
    "is_available": true,
    "learners": 1
  },
  {
    "id": 2,
    "learning_language": "fr",
    "from_language": "en",
    "title": "French",
    "is_available": false,
    "learners": 0
  },
  {
    "id": 3,
    "learning_language": "de",
    "from_language": "en",
    "title": "German",
    "is_available": false,
    "learners": 0
  }
]
```

**Errors:** `500 internal_error` only.

```bash
curl http://localhost:8000/api/v1/courses
```

---

## GET /api/v1/courses/{course_id}/path

The course's learning path, with the learner's progress: every unit, its nodes, and each node's state. The
`/learn` page draws the path from this.

**Request:** `course_id` in the URL, the `id` of an available course (the learner's is `me.active_course.id`).

**Response `200 OK`:** a [Path](#path). Unit 1 of the seeded learner (Units 2 and 3 have the same shape, all
`locked`):

```json
{
  "course": {
    "id": 1,
    "learning_language": "es",
    "from_language": "en",
    "title": "Spanish",
    "is_available": true
  },
  "units": [
    {
      "id": 1,
      "position": 1,
      "title": "Greet people and introduce yourself",
      "nodes": [
        { "id": 1, "position": 1, "title": "Say hello", "kind": "lesson", "state": "completed", "lessons_total": 2, "lessons_completed": 2 },
        { "id": 2, "position": 2, "title": "Introduce yourself", "kind": "lesson", "state": "active", "lessons_total": 2, "lessons_completed": 1 },
        { "id": 3, "position": 3, "title": "Treasure chest", "kind": "chest", "state": "locked", "lessons_total": 0, "lessons_completed": 0 },
        { "id": 4, "position": 4, "title": "Meet people", "kind": "lesson", "state": "locked", "lessons_total": 2, "lessons_completed": 0 },
        { "id": 5, "position": 5, "title": "Unit review", "kind": "review", "state": "locked", "lessons_total": 1, "lessons_completed": 0 }
      ]
    }
  ],
  "active_node_id": 2
}
```

**Errors**

| Status | `code` | Cause |
| --- | --- | --- |
| 404 | `course_not_found` | No course has that id |
| 409 | `course_unavailable` | The course is coming soon: `{"error": {"code": "course_unavailable", "message": "French is coming soon."}}` |
| 422 | `validation_error` | The id isn't a whole number (`details[0].loc` is `["path", "course_id"]`, `type` is `int_parsing`) |
| 503 | `learner_missing` | The database has not been seeded |

```bash
curl http://localhost:8000/api/v1/courses/1/path
```

---

## POST /api/v1/skills/{skill_id}/open-chest

Opens the treasure chest the learner has reached (the chest node whose `state` is `active`) and adds its
20 gems to their balance. The chest then counts as completed, so the next node unlocks.

**Request:** `skill_id` in the URL, the chest node's `id`. No body.

**Response `200 OK`**

| Field | Type | Description |
| --- | --- | --- |
| `gems_awarded` | integer | Gems in the chest (20) |
| `gems` | integer | The learner's gem balance after opening |

```json
{
  "gems_awarded": 20,
  "gems": 520
}
```

**Errors**

| Status | `code` | Cause | `message` |
| --- | --- | --- | --- |
| 404 | `skill_not_found` | No path node has that id | "That path node does not exist." |
| 409 | `not_a_chest` | The node is a lesson or review node | "That path node is not a chest." |
| 409 | `skill_locked` | The chest hasn't been reached yet | "Complete the levels above to reach this chest." |
| 409 | `chest_already_opened` | It was opened before | "That chest has already been opened." |
| 422 | `validation_error` | The id isn't a whole number | "The request is invalid." |
| 503 | `learner_missing` | The database has not been seeded | "The default learner has not been seeded yet." |

```bash
curl -X POST http://localhost:8000/api/v1/skills/3/open-chest
```

---

## POST /api/v1/sessions

Starts the next lesson of a path node. The server decides the rest:

- The **active** node plays its next lesson (`mode: "lesson"`): a wrong answer costs a heart, and the
  learner needs at least one heart to start.
- A **completed** node is practiced (`mode: "practice"`): its lessons in turn, no hearts at stake.
- Any other unfinished session of the learner is abandoned, so there is at most one in progress.

**Request body**

```json
{ "skill_id": 2 }
```

**Response `201 Created`:** a [Session](#session). For the seeded learner, lesson 2 of "Introduce yourself":

```json
{
  "id": 4,
  "mode": "lesson",
  "status": "in_progress",
  "started_at": "2026-10-08T12:00:00Z",
  "node": {
    "id": 2,
    "title": "Introduce yourself"
  },
  "lesson_position": 2,
  "lessons_total": 2,
  "exercises": [
    {"id": 19, "type": "multiple_choice", "instruction": "Select the correct meaning", "prompt": "mucho gusto", "prompt_language": "es", "options": [{"id": 63, "text": "thank you"}, {"id": 61, "text": "nice to meet you"}, {"id": 62, "text": "good night"}], "pairs": null},
    {"id": 20, "type": "match_pairs", "instruction": "Select the matching pairs", "prompt": null, "prompt_language": null, "options": [], "pairs": {"left": ["my name is", "and you?", "goodbye", "nice to meet you"], "right": ["adiós", "me llamo", "mucho gusto", "¿y tú?"]}},
    {"id": 21, "type": "word_bank", "instruction": "Write this in Spanish", "prompt": "What is your name?", "prompt_language": "en", "options": [{"id": 69, "text": "te"}, {"id": 68, "text": "Cómo"}, {"id": 70, "text": "llamas"}, {"id": 72, "text": "yo"}, {"id": 71, "text": "soy"}], "pairs": null},
    {"id": 22, "type": "fill_blank", "instruction": "Fill in the blank", "prompt": "Me ___ Ana.", "prompt_language": "es", "options": [{"id": 75, "text": "gusto"}, {"id": 73, "text": "llamo"}, {"id": 74, "text": "soy"}], "pairs": null},
    {"id": 23, "type": "type_answer", "instruction": "Write this in Spanish", "prompt": "Nice to meet you.", "prompt_language": "en", "options": [], "pairs": null},
    {"id": 24, "type": "listen", "instruction": "Tap what you hear", "prompt": "Mucho gusto, Ana.", "prompt_language": "es", "options": [{"id": 79, "text": "soy"}, {"id": 78, "text": "Ana"}, {"id": 77, "text": "gusto"}, {"id": 76, "text": "Mucho"}, {"id": 80, "text": "noches"}], "pairs": null}
  ],
  "completed_exercise_ids": [],
  "hearts": {
    "current": 5,
    "max": 5,
    "next_heart_at": null,
    "regen_minutes": 30
  }
}
```

**Errors**

| Status | `code` | Cause |
| --- | --- | --- |
| 404 | `skill_not_found` | No path node has that id |
| 409 | `skill_locked` | `{"error": {"code": "skill_locked", "message": "Complete the levels above to unlock this."}}` |
| 409 | `not_a_lesson` | `{"error": {"code": "not_a_lesson", "message": "Treasure chests are opened, not played."}}` |
| 409 | `lesson_unavailable` | The lesson has no exercises yet: Units 2 and 3 are "coming soon" |
| 409 | `out_of_hearts` | A lesson needs at least one heart (practice doesn't) |
| 422 | `validation_error` | `skill_id` is missing or not a whole number |

```bash
curl -X POST http://localhost:8000/api/v1/sessions -H "Content-Type: application/json" -d '{"skill_id": 2}'
```

---

## GET /api/v1/sessions/current

The session in progress, as a [Session](#session). The lesson page plays this one, so a refresh carries on where
it was: `completed_exercise_ids` lists what has been answered.

**Errors:** `404 session_not_found` when nothing is in progress:
`{"error": {"code": "session_not_found", "message": "No lesson is in progress."}}`

---

## GET /api/v1/sessions/{session_id}

One of the learner's sessions, in progress or not, as a [Session](#session).

**Errors:** `404 session_not_found`; `422 validation_error` for an id that isn't a whole number.

---

## POST /api/v1/sessions/{session_id}/answers

Grades one answer on the server and returns an [Answer result](#answer-result). Every attempt is stored in
`session_answers`. In a lesson, a wrong answer (or SKIP) costs a heart; a wrong answer can be tried again later
in the same session, so the client puts the exercise back at the end of the lesson.

**Request body:** `exercise_id`, plus the field for the exercise type:

| Type | Field | Example |
| --- | --- | --- |
| `multiple_choice`, `fill_blank` | `option_ids`: the chosen option | `{"exercise_id": 19, "option_ids": [61]}` |
| `word_bank`, `listen` | `option_ids`: the tiles, in order | `{"exercise_id": 21, "option_ids": [68, 69, 70]}` |
| `type_answer` | `text` | `{"exercise_id": 23, "text": "mucho gsto"}` |
| `match_pairs` | `pair`: one attempt, `[left tile, right tile]` | `{"exercise_id": 20, "pair": ["nice to meet you", "mucho gusto"]}` |
| any | `skipped: true` (SKIP) | `{"exercise_id": 22, "skipped": true}` |

Grading ignores case, punctuation (including ¿ and ¡) and spacing. Typed answers also forgive one wrong,
missing or extra letter, or a missing accent (`verdict: "typo"`). Match pairs are graded pair by pair, and a
wrong pair costs a heart, as on Duolingo; the exercise is done when every pair has been matched.

**Response `200 OK`:** an [Answer result](#answer-result). A wrong choice:

```json
{
  "correct": false,
  "verdict": "wrong",
  "solution": "nice to meet you",
  "exercise_completed": false,
  "hearts": {
    "current": 4,
    "max": 5,
    "next_heart_at": "2026-10-08T12:30:00Z",
    "regen_minutes": 30
  }
}
```

A typed answer with a typo ("mucho gsto" for "Mucho gusto."):

```json
{
  "correct": true,
  "verdict": "typo",
  "solution": "Mucho gusto.",
  "exercise_completed": true,
  "hearts": {
    "current": 4,
    "max": 5,
    "next_heart_at": "2026-10-08T12:30:00Z",
    "regen_minutes": 30
  }
}
```

The first of four pairs (`exercise_completed` turns true with the last):

```json
{
  "correct": true,
  "verdict": "correct",
  "solution": null,
  "exercise_completed": false,
  "hearts": {
    "current": 4,
    "max": 5,
    "next_heart_at": "2026-10-08T12:30:00Z",
    "regen_minutes": 30
  }
}
```

**Errors**

| Status | `code` | Cause |
| --- | --- | --- |
| 404 | `session_not_found`, `exercise_not_found` | Unknown session, or an exercise of another lesson |
| 409 | `session_finished` | The session already ended |
| 409 | `exercise_completed` | That exercise was already answered correctly |
| 409 | `out_of_hearts` | No hearts left in a lesson: refill or practice first |
| 422 | `invalid_answer` | `{"error": {"code": "invalid_answer", "message": "Send the chosen options as option_ids."}}` (text sent for a multiple choice) |

---

## POST /api/v1/sessions/{session_id}/complete

Finishes a session once every exercise is answered (listening exercises may be skipped with "Can't listen
now"). It writes an XP event (10 XP for a lesson, 5 for practice), extends the streak if this is the first
finished session of the learner's day, and then either moves the path node on (a lesson) or gives a heart back
(practice). The node is completed with its last lesson, which unlocks the next one.

**Request:** no body.

**Response `200 OK`:** a [Completion](#completion). The seeded learner finishing "Introduce yourself" 2 minutes
later, with one mistake:

```json
{
  "xp_earned": 10,
  "total_xp": 40,
  "xp_today": 10,
  "daily_goal_xp": 20,
  "accuracy": 83,
  "duration_seconds": 125,
  "streak": {
    "length": 4,
    "longest": 4,
    "extended": true
  },
  "hearts": {
    "current": 4,
    "max": 5,
    "next_heart_at": "2026-10-08T12:30:00Z",
    "regen_minutes": 30
  },
  "node": {
    "id": 2,
    "lessons_completed": 2,
    "lessons_total": 2,
    "completed": true
  }
}
```

**Errors**

| Status | `code` | Cause |
| --- | --- | --- |
| 409 | `session_incomplete` | `{"error": {"code": "session_incomplete", "message": "Answer every exercise before finishing the lesson."}}` |
| 409 | `session_finished` | `{"error": {"code": "session_finished", "message": "That lesson session has already ended."}}` |

---

## POST /api/v1/sessions/{session_id}/quit

Leaves a session early ("End session", or "No thanks" when out of hearts). It counts as `failed` if a lesson ran
out of hearts, `abandoned` otherwise. Nothing is earned or lost.

**Response:** `204 No Content`.

**Errors:** `404 session_not_found`; `409 session_finished`.
