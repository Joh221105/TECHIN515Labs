# Claude / agent context — GIX Quick Eligibility Checker (Vite)

Use this file when working in **this folder** (`eligibility-vite-react`) so changes stay aligned with the assignment spec and the sibling Next.js implementation.

## Product spec
- **Authoritative rules:** `../../SPEC.md` (five-sentence spec). Eligibility behavior must match it exactly.

## This stack
- **Vite 6**, **React 19**, **TypeScript**, **plain CSS** (`src/index.css`) — no Tailwind here.
- **Dev:** `npm run dev` → **http://localhost:3011**
- **Build:** `npm run build`

## Code layout
- **`src/eligibility.ts`** — all deterministic eligibility logic (`evaluateEligibility`, types). **Do not** re-encode rules in `App.tsx`.
- **`src/App.tsx`** — form, validation, and **card-based** results (four services). Keep labels/select options in sync with enums in `eligibility.ts`.
- **`src/main.tsx`** — app entry only.

## UX contract
- Three inputs (program, graduation timing, CPT), submit + reset.
- Four outcomes: eligible, not eligible, eligible pending verification, human review required; always show a reason per service.
- Global banner when any row needs pending verification or human review; extra line on resume when the spec requires a human-review banner.
- Accessible: `<label htmlFor=…>` for every control, `aria-live` on the results region.

## Paired implementation
- **Next.js twin:** `../eligibility-nextjs/` (table UI, Tailwind, `src/lib/eligibility.ts`). If you change rules, update **both** `eligibility.ts` files or factor a shared package (only if the user asks).

## What not to add
- No backend, auth, databases, or external APIs for this assignment unless the user explicitly requests them.

## Smoke check
- **Valid:** MSTI, within two quarters, not on CPT → four **Eligible** cards; resume row without the extra human-review banner line.
- **Invalid:** submit with an empty select → validation message, no crash, no results.
