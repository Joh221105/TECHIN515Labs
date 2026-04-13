# Course Petition Review Tool

A workspace for a university advisor to **validate** uploaded syllabi and documents, **merge** valid PDFs, run **AI-assisted comparisons** against a UW course catalog, and **track** petitions in a spreadsheet-style interface.

**Important:** AI output is for advisor reference only. It does **not** make approval or denial decisions.

## Stack

- **Next.js 15** (App Router, TypeScript)
- **SQLite** (`better-sqlite3`) — local database at `./data/petitions.db`
- **Tailwind CSS** — UI
- **pdf-parse**, **pdf-lib** — text extraction and merged PDFs
- **Anthropic Claude API** (`@anthropic-ai/sdk`) — structured extraction and comparison

## Setup

From this directory (`petition-app/`):

1. Install dependencies:

   ```bash
   npm install
   ```

2. Create `.env.local` (see `.env.example`) and set your API key:

   ```bash
   cp .env.example .env.local
   # Edit .env.local and set ANTHROPIC_API_KEY
   ```

3. Seed the UW course catalog (GIX examples). Either:

   ```bash
   npx tsx src/lib/db-seed.ts
   ```

   or `npm run db:seed`.

4. Start the dev server:

   ```bash
   npm run dev
   ```

Open [http://localhost:3000](http://localhost:3000).

## Data directories

On first use, **`./data`** and **`./data/uploads`** are created automatically (when the app opens the database or handles uploads). The `/data` folder is listed in `.gitignore` so local DB and files stay private.

## Scripts

| Command            | Purpose                    |
| ------------------ | -------------------------- |
| `npm run dev`      | Development server         |
| `npm run build`    | Production build           |
| `npm run start`    | Run production server      |
| `npm run db:seed`  | Same as `tsx src/lib/db-seed.ts` |

## AI usage

Claude assists with **extracting** syllabus structure and **comparing** it to catalog courses. Final decisions remain with the advisor and instructors, per university policy and the project spec.
