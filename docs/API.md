# API reference

The backend is a FastAPI app. Every endpoint, request and response is listed below; every example is a real
response from the API, captured on a freshly seeded database with the clock fixed at `2026-10-08T12:00:00Z`.
The seed gives the built-in learner a few days of history (4 lessons finished on the 3 days before), so the
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
| GET | [`/api/v1/courses`](#get-apiv1courses) | The course catalogue |
| GET | [`/api/v1/courses/{course_id}/path`](#get-apiv1coursescourse_idpath) | A course's learning path with the learner's progress |
| POST | [`/api/v1/skills/{skill_id}/open-chest`](#post-apiv1skillsskill_idopen-chest) | Open a treasure chest on the path |

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
| 404 | `course_not_found` | No course has that id | `PATCH /api/v1/me`, `GET .../courses/{id}/path` |
| 404 | `skill_not_found` | No path node has that id | `POST .../skills/{id}/open-chest` |
| 405 | `method_not_allowed` | The path exists but not with this method | Any URL |
| 409 | `course_unavailable` | The course exists but is "coming soon" | `PATCH /api/v1/me`, `GET .../courses/{id}/path` |
| 409 | `not_a_chest` | The path node isn't a treasure chest | `POST .../skills/{id}/open-chest` |
| 409 | `skill_locked` | The chest hasn't been reached yet | `POST .../skills/{id}/open-chest` |
| 409 | `chest_already_opened` | The chest was opened before | `POST .../skills/{id}/open-chest` |
| 422 | `validation_error` | The body is not valid JSON, has an invalid value or an unknown field, or an id in the URL isn't a whole number | `PATCH /api/v1/me`, endpoints with an id in the URL |
| 500 | `internal_error` | An unexpected server error (the details are logged on the server, never sent) | Any endpoint |
| 503 | `learner_missing` | The database has not been seeded with the built-in learner | Every endpoint that acts as the learner |

Each entry in `details` describes one problem:

| Field | Description |
| --- | --- |
| `type` | Kind of problem, e.g. `literal_error`, `extra_forbidden`, `json_invalid`, `value_error`, `int_parsing` |
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
| `joined_at` | datetime | When the learner was created |
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
  "total_xp": 40,
  "xp_today": 0,
  "lessons_completed": 4,
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

Changes the learner's own preferences. Used by the "Get started" flow (course, daily goal, time zone) and later
by the settings page. Send only the fields you want to change.

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
  "total_xp": 40,
  "xp_today": 0,
  "lessons_completed": 4,
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
        { "id": 1, "position": 1, "title": "Say hello", "kind": "lesson", "state": "completed", "lessons_total": 3, "lessons_completed": 3 },
        { "id": 2, "position": 2, "title": "Introduce yourself", "kind": "lesson", "state": "active", "lessons_total": 3, "lessons_completed": 1 },
        { "id": 3, "position": 3, "title": "Treasure chest", "kind": "chest", "state": "locked", "lessons_total": 0, "lessons_completed": 0 },
        { "id": 4, "position": 4, "title": "Meet people", "kind": "lesson", "state": "locked", "lessons_total": 3, "lessons_completed": 0 },
        { "id": 5, "position": 5, "title": "Unit review", "kind": "review", "state": "locked", "lessons_total": 2, "lessons_completed": 0 }
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
