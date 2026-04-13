# Part 3: Comparison, Testing, and `.cursorrules` Rerun Notes

## Implementation sources

| Folder | Tooling | Stack |
|--------|---------|--------|
| `implementations/eligibility-nextjs/` | **Cursor** (note the model from your Cursor model picker for that session) | Next.js 15, React 19, TypeScript, Tailwind CSS 4 |
| `implementations/eligibility-vite-react/` | **Cursor + Claude Opus 4.6** | Vite 6, React 19, TypeScript, plain CSS |

Both implement the **same** functional requirements in [`SPEC.md`](./SPEC.md). Rules live in `src/lib/eligibility.ts` (Next.js) and `src/eligibility.ts` (Vite); logic is aligned. The Next.js app uses a **data table**; the Vite app uses **stacked cards** and a different visual theme (serif headline, green accent) to reflect a separate generation pass.

**AI helper config:** Package-wide guidance is in [`.cursorrules`](./.cursorrules). The Next app also has [`implementations/eligibility-nextjs/.cursorrules`](./implementations/eligibility-nextjs/.cursorrules). The Vite app includes [`implementations/eligibility-vite-react/claude.md`](./implementations/eligibility-vite-react/claude.md) for Claude- or agent-oriented context (stack, files, smoke checks).

## Comparison table

| Dimension | Next.js (Cursor) | Vite + React (Cursor, Claude Opus 4.6) |
|-----------|------------------|----------------------------------------|
| **Spec fidelity** | Four services, alumni block, global + resume banners | Same outcomes and copy from shared rule structure |
| **Maintainability** | App Router + `@/` alias; rules isolated in `lib/` | Single-page `App.tsx`; rules in `src/eligibility.ts` |
| **UX / layout** | Tailwind, compact table | Plain CSS, card list, distinct typography |
| **Bundle / tooling** | Next build, SSR-capable stack | Vite SPA, fast dev server |
| **Input validation** | Submit with empty fields → inline alert; no throws | Same behavior |
| **Accessibility** | Labels, `aria-live` on results | Labels, `aria-live` on results |
| **Risk of drift** | Two copies of `eligibility.ts` must stay in sync when rules change | Same |
| **AI project docs** | [`.cursorrules`](./.cursorrules) (package) + [`eligibility-nextjs/.cursorrules`](./implementations/eligibility-nextjs/.cursorrules) | [`claude.md`](./implementations/eligibility-vite-react/claude.md) |

## `.cursorrules` rerun — observed differences

The package [`.cursorrules`](./.cursorrules) and the Next-specific [`implementations/eligibility-nextjs/.cursorrules`](./implementations/eligibility-nextjs/.cursorrules) ask for: pure rule module, no backend, strong validation, visible human-review banners, and accessibility.

**Without** such a file, a typical first-pass AI layout often (a) inlines conditional logic inside JSX or a single giant `onSubmit`, (b) omits a global “pending verification” banner, or (c) uses `alert()` for errors.

**With** `.cursorrules` active for the Next.js (Cursor) pass, that app:

- Keeps **all** eligibility decisions in `src/lib/eligibility.ts`.
- Uses **non-throwing** validation (`evaluateEligibility` returns `null` when inputs are incomplete; the UI gates submit).
- Renders **global** amber banners when any row is `pending_verification` or `human_review`, plus per-row resume banners when required.

The **Claude Opus 4.6 / Vite** build follows the same rule module pattern and banner behavior; differences are mostly **framework and presentation**. For future edits to that app, [`claude.md`](./implementations/eligibility-vite-react/claude.md) summarizes spec paths, file roles, and parity with the Next app.

If you regenerate the Next.js app in Cursor **without** the package or Next `.cursorrules`, compare those three bullets first—they are the usual deltas.

## Smoke tests (does it run, core path, invalid input safe?)

### Next.js (`eligibility-nextjs`)

| Check | Result |
|-------|--------|
| **Install / build** | `npm install` then `npm run build` — completes without errors. |
| **Run** | `npm run dev` — port **3010** — home page loads. |
| **Core path** | MSTI + within two quarters + not on CPT → all four services **Eligible** (resume without human-review sub-banner). |
| **Invalid input** | Submit with any field empty → validation message; no crash. |

**Commands:**

```bash
cd implementations/eligibility-nextjs
npm install
npm run build
```

### Vite (`eligibility-vite-react`)

| Check | Result |
|-------|--------|
| **Install / build** | `npm install` then `npm run build` — completes without errors. |
| **Run** | `npm run dev` — port **3011** — form and results region work. |
| **Core path** | Same as Next.js: MSTI / WITHIN_2 / NONE → four **Eligible** cards. |
| **Invalid input** | Empty submit → validation message; no crash. |

**Commands:**

```bash
cd implementations/eligibility-vite-react
npm install
npm run build
```

## Input testing (1 valid + 1 invalid per implementation)

### Valid input (both apps)

| Field | Value |
|-------|--------|
| Program | MSTI |
| Graduation | Within the next two quarters |
| CPT | Not on CPT |

**Expected:** All four services → **Eligible**; no global human-review banner; resume **without** the extra “Human review banner” line.

**Observed:** Matches after `npm run build` and manual UI check.

### Invalid input (both apps)

| Field | Value |
|-------|--------|
| Program | *(leave default “Select program…”) |
| Graduation | Within the next two quarters |
| CPT | Not on CPT |

**Expected:** Validation message; no results; no crash.

**Observed:** Inline validation; results not shown.

---

## Suggested wording for your write-up

- **Two tools / models:** Implementation A — Cursor (record your model). Implementation B — **Cursor with Claude Opus 4.6**. Both received **verbatim** [`SPEC.md`](./SPEC.md).
- **Artifact map:** `SPEC.md`, `FLOWCHART.md`, `.cursorrules`, `implementations/eligibility-nextjs/` (including `.cursorrules`), `implementations/eligibility-vite-react/` (including `claude.md`), and this file.
