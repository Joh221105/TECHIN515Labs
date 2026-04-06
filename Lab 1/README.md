# Lab 1

This folder contains two Streamlit apps:

| App | How to run | Notes |
|-----|------------|--------|
| **ProcureGIX** | `cd "Lab 1"` then `streamlit run app.py` | Uses `procuregix/`, `db.py`, and `Lab 1/.streamlit/`. |
| **Wayfinder** | `cd "Lab 1/Wayfinder"` then `streamlit run app.py` | Separate app; theme lives in `Wayfinder/.streamlit/` (Streamlit reads config from your **current working directory**). |

You can use **one** virtualenv for both apps (`python3 -m venv .venv` in `Lab 1`, then `pip install -r requirements.txt`). Activate it before running either app.

---

# ProcureGIX

**ProcureGIX** is a Streamlit web app for **UW MSTI**–style **purchase requests**. Students submit order line items by class and team; instructors approve or reject them; program staff use the admin area for terms, exports, and instructor accounts. Data lives in a local **SQLite** database.

---

## What you need

- **Python 3.10+** (3.11–3.13 work well)
- **pip** and a virtual environment (recommended)

---

## Install

This app is in the **`Lab 1`** folder inside the repo. From the **repository root**:

```bash
cd "Lab 1"
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If you already opened a terminal **inside `Lab 1`**, you can skip `cd "Lab 1"`.

If you see errors importing **pandas**, install it explicitly:

```bash
pip install pandas
```

---

## Run the app

Run this **from the `Lab 1` directory** (so `app.py`, `db.py`, and `.streamlit/` are found):

```bash
cd "Lab 1"    # if you are not already here
streamlit run app.py
```

Your browser should open. The UI title is **UW MSTI**; the app name in the tab is **ProcureGIX**.

- **Entry point:** `app.py` (page config + calls into `procuregix.main`).
- **First launch:** `init_db()` creates or updates `procuregix.db` next to `db.py` in this folder.

---

## Database

| Item | Location |
|------|----------|
| SQLite file | `Lab 1/procuregix.db` (next to `Lab 1/db.py`) |
| Schema / logic | `Lab 1/db.py` |

To **reset all data**, stop the app, delete `procuregix.db` inside **`Lab 1`** (and `procuregix.db-wal` / `procuregix.db-shm` if they exist), then start the app again so a fresh database is created.

---

## How to use the app

At the top of the main screen, choose a **Role**: **Student**, **Teacher**, or **Admin**.

### Admin (use first in a new setup)

There is **no separate admin login** in this project—anyone who selects **Admin** can use that area. Use it only in trusted environments (e.g. local machine or private network).

**Suggested first steps**

1. Open **Instructor account** in the sidebar and create at least one **teacher** (email, display name, initial password).
2. Sign out of the browser session or switch role; the teacher signs in as **Teacher** with that account.

**Admin sidebar**

| Item | What it’s for |
|------|----------------|
| **Archive** | Quarters that were archived; open a quarter to review classes/orders or **restore** it to the main **Classes** tabs. |
| **Classes** | Tabs per active term; each class is an expander with orders, **Save changes** (status + ongoing/completed), and optional **Archive quarter** on the class card. |
| **Instructor account** | Create additional teacher logins. |
| **All orders** | Full list with optional filters (Class, Status, Provider); leave filters empty to show everything; **Download data as CSV**. |

---

### Teacher

1. Select **Teacher** and sign in with credentials **created by an admin**.
2. Use the **sidebar**:
   - **Orders** — Pending, Rejected, Approved. Use **Filter by Class** (optional; empty = all classes). Approve or reject pending lines (reject requires feedback).
   - **Classes** — Add classes (name, budget, quarter, enrollment passcode), view passcode and roster (expand **Registered students**), delete a class when needed.
   - **Change password** — Update password.
   - **Log out**

Students enroll with the **passcode** you set on each class.

---

### Student

1. Select **Student**.
2. **Create account** or **Sign in**  
   - Registration requires a **UW `@uw.edu`** email.  
   - After first login you may be asked to enter **first and last name** for how they should appear on requests.
3. **Sidebar**
   - **Notifications** — Alerts related to your orders (e.g. rejections).
   - **My Classes** — Budgets and orders per enrolled class; **New Order** from a class.
   - **All Orders** — All your lines across classes.
   - **Enroll in a class** — Pick class, team number/name, **enrollment passcode** from the instructor.
   - **Change password**
   - **Log out**

4. Submit orders from **My Classes**; track status and budgets there or under **All Orders**.

---

## Typical workflow (short)

1. **Admin** creates **teacher** accounts.  
2. **Teacher** creates **classes** (budget, quarter, passcode).  
3. **Student** registers, **enrolls** with passcode, submits **orders**.  
4. **Teacher** **approves** or **rejects** under **Orders**.  
5. **Admin** monitors **Classes** / **All orders** and archives terms under **Archive** when appropriate.

---

## Project layout

All paths are under **`Lab 1/`** in the repository.

| Path | Role |
|------|------|
| `Lab 1/Wayfinder/app.py` | **Wayfinder** Streamlit entry (run from `Lab 1/Wayfinder`) |
| `Lab 1/app.py` | **ProcureGIX** Streamlit entry + page config |
| `Lab 1/db.py` | SQLite connection, schema, all data access |
| `Lab 1/procuregix/main.py` | Role routing, `init_db()` on each run |
| `Lab 1/procuregix/ui/student/` | Login, dashboard, orders, sidebar |
| `Lab 1/procuregix/ui/teacher/` | Teacher auth and dashboard |
| `Lab 1/procuregix/ui/admin/` | Admin dashboard, sidebar, instructor form |
| `Lab 1/procuregix/config.py` | Quarters, statuses, providers, etc. |

---

## Security note

**Admin** is not password-protected in code. Do not expose this app to the public internet without adding authentication and other hardening for the admin role.

---

## Troubleshooting

- **Blank or stale UI after code changes:** refresh the browser; Streamlit may keep **session state**—switch role or clear session if something looks wrong.
- **Database locked:** ensure only one Streamlit process is using `procuregix.db`.
- **Import errors:** confirm the virtualenv is active and run `pip install -r requirements.txt` (and `pip install pandas` if needed).
