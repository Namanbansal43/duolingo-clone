# Duolingo Clone

A full-stack Duolingo-style learning app built for an SDE assignment.

| Part | Stack | Status |
| --- | --- | --- |
| `frontend/` | Next.js 16 (App Router, TypeScript), Tailwind CSS v4 | Landing page done |
| `backend/` | Python FastAPI, SQLite | Not started |

## Running the frontend

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

## Brand assets

The logo, flags, illustrations and animations in `frontend/public/landing/` are Duolingo's own artwork. They are
used here only to reproduce the look of duolingo.com for a non-commercial assignment, and remain the property of
Duolingo, Inc. This project is not affiliated with Duolingo. To rebrand, replace that folder; no code changes are
needed.

Duolingo's typefaces are proprietary, so the app uses Signika and Fredoka from Google Fonts as stand-ins.
