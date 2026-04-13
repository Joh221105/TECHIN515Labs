# Quick Eligibility Checker (Vite + React)

Second implementation for the assignment: **Cursor** with **Claude Opus 4.6** (select this model in Cursor’s model picker for the chat/agent that generated this variant).

- **Stack:** Vite 6, React 19, TypeScript; plain CSS (no Tailwind).
- **Rules:** `src/eligibility.ts` mirrors [`../../SPEC.md`](../../SPEC.md) and matches `eligibility-nextjs` logic.
- **UI:** Card-based results (contrasts with the Next.js table layout).
- **Agent notes:** See [`claude.md`](./claude.md) for spec location, file layout, accessibility expectations, and keeping rules in sync with `eligibility-nextjs`.

```bash
npm install
npm run dev
```

Dev server: `http://localhost:3011`

```bash
npm run build
```
