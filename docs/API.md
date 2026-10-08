# API reference

The backend is a FastAPI app. Every endpoint, request and response is listed below; every example is a real
response from the API, captured with the clock fixed at `2026-10-08T12:00:00Z`.

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
| 404 | `course_not_found` | `active_course_id` doesn't match a course | `PATCH /api/v1/me` |
| 405 | `method_not_allowed` | The path exists but not with this method | Any URL |
| 409 | `course_unavailable` | The course exists but is "coming soon" | `PATCH /api/v1/me` |
| 422 | `validation_error` | The body is not valid JSON, has an invalid value, or has an unknown field | `PATCH /api/v1/me` |
| 500 | `internal_error` | An unexpected server error (the details are logged on the server, never sent) | Any endpoint |
| 503 | `learner_missing` | The database has not been seeded with the built-in learner | `GET`, `PATCH /api/v1/me` |

Each entry in `details` describes one problem:

| Field | Description |
| --- | --- |
| `type` | Kind of problem, e.g. `literal_error`, `extra_forbidden`, `json_invalid`, `value_error` |
| `loc` | Where it is: `["body", "<field>"]` |
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
  "joined_at": "2026-10-08T12:00:00Z",
  "timezone": "UTC",
  "active_course": {
    "id": 1,
    "learning_language": "es",
    "from_language": "en",
    "title": "Spanish",
    "is_available": true
  },
  "daily_goal_xp": 20,
  "total_xp": 1240,
  "gems": 500,
  "hearts": {
    "current": 4,
    "max": 5,
    "next_heart_at": "2026-10-08T12:20:00Z",
    "regen_minutes": 30
  },
  "streak": {
    "length": 6,
    "extended_today": true,
    "longest": 14
  }
}
```

A freshly seeded learner has `total_xp: 0`, full hearts with `next_heart_at: null`, and a streak of
`{"length": 0, "extended_today": false, "longest": 0}`.

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
  "total_xp": 1240,
  "gems": 500,
  "hearts": {
    "current": 4,
    "max": 5,
    "next_heart_at": "2026-10-08T12:20:00Z",
    "regen_minutes": 30
  },
  "streak": {
    "length": 6,
    "extended_today": true,
    "longest": 14
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
