# Project Context

## What This Project Is

A **TECHIN 510** lab repository containing **two Streamlit web apps** under `Lab 1/`: **ProcureGIX** (student/instructor/admin workflows for class purchase requests and budgets, backed by SQLite) and **Wayfinder** (a GIX campus resource finder with search, filters, and optional maps).

## Tech Stack

- **Python** 3.11+ (3.10+ also works per Lab 1 docs; prefer 3.11+ features where used)
- **Streamlit** for the web UI
- **SQLite** for ProcureGIX persistence (`db.py`, local `.db` files; gitignored)
- **Pandas** for tabular data (e.g. Wayfinder maps); install via `requirements.txt` / `pip install pandas` if needed
- **Plotly** for interactive charts when you add them (not required for the current baseline UIs)

## Project Structure

- **`Lab 1/app.py`** — ProcureGIX entrypoint (`streamlit run app.py` from `Lab 1/`)
- **`Lab 1/procuregix/`** — ProcureGIX package (`main.py`, `ui/`, `auth/`, `config.py`, etc.)
- **`Lab 1/db.py`** — SQLite initialization and schema helpers for ProcureGIX
- **`Lab 1/.streamlit/`** — Streamlit theme/config for ProcureGIX when run from `Lab 1/`
- **`Lab 1/requirements.txt`** — Shared Python dependencies for Lab 1
- **`Lab 1/Wayfinder/app.py`** — Wayfinder entrypoint (run from `Lab 1/Wayfinder/` so that folder’s `.streamlit/` is picked up)
- **`Lab 1/Wayfinder/`** — Wayfinder-only modules (e.g. `search_heading.py`, tests)
- **`.cursor/rules/`** — Cursor rules (e.g. `lab1-streamlit.mdc` for Python under `Lab 1/`)

There is **no** single top-level `utils.py` or `data/` folder for the whole repo; helpers live next to each app (e.g. `procuregix/utils/`, Wayfinder modules).

## Development Commands

From the **repository root**:

```bash
cd "Lab 1"
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**ProcureGIX** (must be run from `Lab 1/`):

```bash
cd "Lab 1"
streamlit run app.py
```

**Wayfinder** (run from `Lab 1/Wayfinder/` so Streamlit uses `Wayfinder/.streamlit/config.toml`):

```bash
cd "Lab 1/Wayfinder"
streamlit run app.py
```

## Coding Standards

- Follow **PEP 8** and keep code readable
- Use **type hints** on function signatures (especially public APIs and non-trivial helpers)
- Use **Google-style docstrings** for non-trivial functions
- **Never hardcode** secrets (API keys, passwords, tokens). Use env vars, `.env` (gitignored), or Streamlit secrets as appropriate
- Handle errors **gracefully**: prefer specific `except` clauses, `logging` for diagnostics, and `st.error` / `st.warning` / `st.info` for user-visible messages—avoid bare `except:` and avoid crashing the whole app on bad input where recovery is possible
- Escape user-controlled strings when embedding in HTML (`html.escape`) if using `unsafe_allow_html=True`

## Important Notes

- This is **course work** for **TECHIN 510** at **UW GIX**
- **Audience:** **ProcureGIX** — MSTI/GIX students submitting purchase requests, instructors managing classes and approvals, program staff using admin tools. **Wayfinder** — anyone browsing GIX campus resources (demo/illustrative data)
- After substantive changes, **smoke-test** the app you touched: ProcureGIX with `streamlit run app.py` from `Lab 1/`, Wayfinder with `streamlit run app.py` from `Lab 1/Wayfinder/`
- Root **`README.md`** may still mention another course code; treat **`TECHIN510Labs`** and this file as the source of truth for **TECHIN 510** context when they differ
