# GIX Career Services — Quick Eligibility Checker (Assignment Package)

This folder contains the **engineering business & design** assignment artifacts: specification, flowchart, AI project rules, **two** implementations, and comparison/testing notes.

## Contents

| File / folder | Purpose |
|---------------|---------|
| [`SPEC.md`](./SPEC.md) | **Part 1** — Five-sentence specification (give verbatim to both AI tools). |
| [`FLOWCHART.md`](./FLOWCHART.md) | **Part 1** — Decision flowchart (Mermaid) + human-review callouts. |
| [`.cursorrules`](./.cursorrules) | **Part 2** — Package-level Cursor rules (shared scope for this assignment folder). |
| [`implementations/eligibility-nextjs/.cursorrules`](./implementations/eligibility-nextjs/.cursorrules) | Next.js–specific Cursor rules (paths, App Router, Tailwind, `src/lib/eligibility.ts`). |
| [`implementations/eligibility-nextjs/`](./implementations/eligibility-nextjs/) | **Implementation A** — Next.js 15 + TypeScript + Tailwind (Cursor; note the model you used in Cursor). |
| [`implementations/eligibility-vite-react/`](./implementations/eligibility-vite-react/) | **Implementation B** — Vite 6 + React + TypeScript + plain CSS; built with **Cursor + Claude Opus 4.6** (see folder README). |
| [`implementations/eligibility-vite-react/claude.md`](./implementations/eligibility-vite-react/claude.md) | Agent context for the Vite app (spec path, layout, smoke checks, sync with Next.js). |
| [`COMPARISON_AND_TESTING.md`](./COMPARISON_AND_TESTING.md) | **Part 3** — Comparison table, smoke tests, input tests, `.cursorrules` notes. |

## Quick run

**Next.js (port 3010)**

```bash
cd implementations/eligibility-nextjs
npm install
npm run dev
```

Open `http://localhost:3010`.

**Vite + React (port 3011)**

```bash
cd implementations/eligibility-vite-react
npm install
npm run dev
```

Open `http://localhost:3011`.

## Assignment note

If your instructor requires **two different products** (e.g. Cursor vs ChatGPT), regenerate one implementation with that tool; this repo currently documents **two Cursor sessions with different models** (default/other vs **Claude Opus 4.6** for the Vite app).
