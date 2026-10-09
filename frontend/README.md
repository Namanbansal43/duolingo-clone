# Frontend

The Next.js 16 (TypeScript, Tailwind CSS v4) frontend of the Duolingo clone.

```bash
npm install
npm run dev     # http://localhost:3000; start the backend first (http://localhost:8000)
```

The browser calls `/api/...` on this site and Next.js forwards it to the backend (`API_URL`, see
`.env.example`). Setup, architecture and features are in the [project README](../README.md); the page-by-page
build notes are in [DOCUMENTATION.md](../DOCUMENTATION.md).
