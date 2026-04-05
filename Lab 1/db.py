"""SQLite persistence for ProcureGIX."""

from __future__ import annotations

import hashlib
import secrets as secrets_std
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "procuregix.db"

# Student-facing accounts must use a UW email address (self-service registration and admin-created).
UW_STUDENT_EMAIL_SUFFIX = "@uw.edu"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, decl: str) -> None:
    info = conn.execute(f"PRAGMA table_info({table})").fetchall()
    names = {row[1] for row in info}
    if column not in names:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                class_name TEXT NOT NULL,
                team_number INTEGER NOT NULL,
                cfo_name TEXT NOT NULL,
                provider TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit_price REAL NOT NULL,
                link_url TEXT NOT NULL,
                notes TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
            """
        )
        _ensure_column(conn, "orders", "order_group_id", "TEXT")
        _ensure_column(conn, "orders", "attention_message", "TEXT")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS class_budgets (
                class_name TEXT PRIMARY KEY,
                budget_usd REAL NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS teacher_classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL UNIQUE,
                budget_usd REAL NOT NULL,
                teacher_name TEXT NOT NULL
            )
            """
        )
        _ensure_column(conn, "teacher_classes", "enroll_passcode", "TEXT")
        _ensure_column(conn, "teacher_classes", "quarter", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "orders", "admin_fulfillment", "TEXT NOT NULL DEFAULT 'ongoing'")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_archived_quarters (
                quarter TEXT PRIMARY KEY
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS student_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL DEFAULT '',
                last_name TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        _ensure_column(conn, "student_accounts", "first_name", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "student_accounts", "last_name", "TEXT NOT NULL DEFAULT ''")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS student_enrollments (
                student_id INTEGER NOT NULL,
                class_name TEXT NOT NULL,
                cfo_name TEXT NOT NULL,
                team_number INTEGER NOT NULL,
                team_name TEXT NOT NULL,
                enrolled_at TEXT NOT NULL,
                visible_on_student_dashboard INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (student_id, class_name),
                FOREIGN KEY (student_id) REFERENCES student_accounts(id)
            )
            """
        )
        _ensure_column(
            conn,
            "student_enrollments",
            "visible_on_student_dashboard",
            "INTEGER NOT NULL DEFAULT 1",
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS teacher_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                display_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        _ensure_column(conn, "teacher_accounts", "username", "TEXT")
        cols = {row[1] for row in conn.execute("PRAGMA table_info(teacher_accounts)").fetchall()}
        if "username" in cols and "email" in cols:
            conn.execute(
                """
                UPDATE teacher_accounts SET username = lower(trim(email))
                WHERE username IS NULL OR trim(coalesce(username, '')) = ''
                """
            )

        _migrate_legacy_student_schema(conn)


def _student_enrollment_columns(conn: sqlite3.Connection) -> set[str]:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='student_enrollments'"
    )
    if cur.fetchone() is None:
        return set()
    return {row[1] for row in conn.execute("PRAGMA table_info(student_enrollments)").fetchall()}


def _student_account_columns(conn: sqlite3.Connection) -> set[str]:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='student_accounts'"
    )
    if cur.fetchone() is None:
        return set()
    return {row[1] for row in conn.execute("PRAGMA table_info(student_accounts)").fetchall()}


def _slim_student_accounts_table(conn: sqlite3.Connection) -> None:
    cols = _student_account_columns(conn)
    if "cfo_name" not in cols:
        return
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.executescript(
        """
        CREATE TABLE student_accounts_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL DEFAULT '',
            last_name TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        INSERT INTO student_accounts_new (
            id, email, password_salt, password_hash, first_name, last_name, created_at
        )
        SELECT id, email, password_salt, password_hash, '', '', created_at FROM student_accounts;
        DROP TABLE student_accounts;
        ALTER TABLE student_accounts_new RENAME TO student_accounts;
        """
    )


def _migrate_legacy_student_schema(conn: sqlite3.Connection) -> None:
    """Move CFO/team from student_accounts into per-class enrollments; add student_id PK."""
    enc = _student_enrollment_columns(conn)
    if not enc:
        return
    if "student_id" in enc:
        _slim_student_accounts_table(conn)
        return

    conn.execute("PRAGMA foreign_keys=OFF")
    _ensure_column(conn, "student_enrollments", "student_id", "INTEGER")
    _ensure_column(conn, "student_enrollments", "team_number", "INTEGER")
    _ensure_column(conn, "student_enrollments", "team_name", "TEXT")

    conn.execute(
        """
        UPDATE student_enrollments SET student_id = (
            SELECT sa.id FROM student_accounts sa
            WHERE sa.cfo_name = student_enrollments.cfo_name LIMIT 1
        )
        """
    )
    conn.execute(
        """
        UPDATE student_enrollments SET team_number = (
            SELECT sa.team_number FROM student_accounts sa WHERE sa.id = student_enrollments.student_id
        )
        WHERE student_id IS NOT NULL AND team_number IS NULL
        """
    )
    conn.execute(
        """
        UPDATE student_enrollments SET team_name = (
            SELECT sa.team_name FROM student_accounts sa WHERE sa.id = student_enrollments.student_id
        )
        WHERE student_id IS NOT NULL AND (team_name IS NULL OR trim(COALESCE(team_name, '')) = '')
        """
    )
    conn.execute("DELETE FROM student_enrollments WHERE student_id IS NULL")
    conn.execute(
        "UPDATE student_enrollments SET team_number = 1 WHERE team_number IS NULL"
    )
    conn.execute(
        """
        UPDATE student_enrollments SET team_name = '—'
        WHERE team_name IS NULL OR trim(team_name) = ''
        """
    )

    conn.executescript(
        """
        CREATE TABLE student_enrollments_new (
            student_id INTEGER NOT NULL,
            class_name TEXT NOT NULL,
            cfo_name TEXT NOT NULL,
            team_number INTEGER NOT NULL,
            team_name TEXT NOT NULL,
            enrolled_at TEXT NOT NULL,
            visible_on_student_dashboard INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (student_id, class_name)
        );
        INSERT INTO student_enrollments_new (
            student_id, class_name, cfo_name, team_number, team_name,
            enrolled_at, visible_on_student_dashboard
        )
        SELECT
            student_id,
            class_name,
            cfo_name,
            team_number,
            team_name,
            enrolled_at,
            COALESCE(visible_on_student_dashboard, 1)
        FROM student_enrollments;
        DROP TABLE student_enrollments;
        ALTER TABLE student_enrollments_new RENAME TO student_enrollments;
        """
    )
    _slim_student_accounts_table(conn)


def _teacher_account_columns(conn: sqlite3.Connection) -> set[str]:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='teacher_accounts'"
    )
    if cur.fetchone() is None:
        return set()
    return {row[1] for row in conn.execute("PRAGMA table_info(teacher_accounts)").fetchall()}


def _hash_teacher_password(password: str) -> tuple[str, str]:
    salt = secrets_std.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("ascii"),
        600_000,
        dklen=32,
    )
    return salt, dk.hex()


def _verify_teacher_password(password: str, salt: str, hash_hex: str) -> bool:
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("ascii"),
        600_000,
        dklen=32,
    )
    return secrets_std.compare_digest(dk.hex(), hash_hex)


def admin_create_teacher_account(
    username: str, password: str, display_name: str
) -> tuple[bool, str]:
    """Provision an instructor login (admin only in UI). Username stored lowercased."""
    un = username.strip().lower()
    display_n = display_name.strip()
    if len(un) < 2:
        return False, "Username must be at least 2 characters."
    if any(c.isspace() for c in un):
        return False, "Username cannot contain spaces."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not display_n:
        return False, "Display name is required."
    salt, pw_hash = _hash_teacher_password(password)
    ts = utc_now_iso()
    try:
        with get_conn() as conn:
            cols = _teacher_account_columns(conn)
            if "username" not in cols:
                conn.execute(
                    """
                    INSERT INTO teacher_accounts (email, password_salt, password_hash, display_name, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (un, salt, pw_hash, display_n, ts),
                )
            else:
                fields = [
                    "username",
                    "password_salt",
                    "password_hash",
                    "display_name",
                    "created_at",
                ]
                values: list = [un, salt, pw_hash, display_n, ts]
                if "email" in cols:
                    fields.insert(1, "email")
                    values.insert(1, un)
                ph = ",".join("?" * len(fields))
                conn.execute(
                    f"INSERT INTO teacher_accounts ({','.join(fields)}) VALUES ({ph})",
                    values,
                )
    except sqlite3.IntegrityError:
        return False, "That username is already taken."
    return True, ""


def verify_teacher_account(username: str, password: str) -> dict | None:
    """Return account dict if credentials match, else None."""
    un = username.strip().lower()
    if not un:
        return None
    with get_conn() as conn:
        cols = _teacher_account_columns(conn)
        row = None
        if "username" in cols:
            row = conn.execute(
                """
                SELECT id, username, display_name, password_salt, password_hash
                FROM teacher_accounts WHERE lower(username) = ?
                """,
                (un,),
            ).fetchone()
            if row is None and "email" in cols:
                row = conn.execute(
                    """
                    SELECT id, email AS username, display_name, password_salt, password_hash
                    FROM teacher_accounts WHERE lower(email) = ?
                    """,
                    (un,),
                ).fetchone()
        else:
            row = conn.execute(
                """
                SELECT id, email AS username, display_name, password_salt, password_hash
                FROM teacher_accounts WHERE lower(email) = ?
                """,
                (un,),
            ).fetchone()
    if row is None:
        return None
    if not _verify_teacher_password(
        password, str(row["password_salt"]), str(row["password_hash"])
    ):
        return None
    return {
        "id": int(row["id"]),
        "username": str(row["username"]),
        "display_name": str(row["display_name"]),
    }


def change_teacher_password(
    *, username: str, current_password: str, new_password: str
) -> tuple[bool, str]:
    if len(new_password) < 8:
        return False, "New password must be at least 8 characters."
    acct = verify_teacher_account(username, current_password)
    if acct is None:
        return False, "Current password is incorrect."
    salt, pw_hash = _hash_teacher_password(new_password)
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE teacher_accounts SET password_salt = ?, password_hash = ?
            WHERE id = ?
            """,
            (salt, pw_hash, int(acct["id"])),
        )
    return True, ""


def fetch_teacher_accounts_summary() -> list[dict]:
    with get_conn() as conn:
        cols = _teacher_account_columns(conn)
        if not cols:
            return []
        if "username" in cols:
            rows = conn.execute(
                """
                SELECT id, username, display_name, created_at
                FROM teacher_accounts
                ORDER BY username COLLATE NOCASE
                """
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, email AS username, display_name, created_at
                FROM teacher_accounts
                ORDER BY email COLLATE NOCASE
                """
            ).fetchall()
    return [dict(r) for r in rows]


def student_roster_display_name(first_name: str, last_name: str) -> str:
    """Full name for CFO / order labels: trimmed first + last, single space."""
    parts = [(first_name or "").strip(), (last_name or "").strip()]
    return " ".join(p for p in parts if p)


def is_valid_uw_student_email(email: str) -> bool:
    """True if the address is a simple @uw.edu mailbox (case-insensitive)."""
    em = email.strip().lower()
    if len(em) < len(UW_STUDENT_EMAIL_SUFFIX) + 2:
        return False
    if "@" not in em:
        return False
    return em.endswith(UW_STUDENT_EMAIL_SUFFIX)


def admin_create_student_account(
    email: str, password: str, first_name: str, last_name: str
) -> tuple[bool, str]:
    """Provision a student login. Email lowercased @uw.edu; name used as roster/CFO when enrolling."""
    em = email.strip().lower()
    fn = first_name.strip()
    ln = last_name.strip()
    if not is_valid_uw_student_email(em):
        return False, f"Student email must be a UW address ending in {UW_STUDENT_EMAIL_SUFFIX}."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not fn:
        return False, "First name is required."
    if not ln:
        return False, "Last name is required."
    salt, pw_hash = _hash_teacher_password(password)
    ts = utc_now_iso()
    try:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO student_accounts (
                    email, password_salt, password_hash, first_name, last_name, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (em, salt, pw_hash, fn, ln, ts),
            )
    except sqlite3.IntegrityError:
        return False, "That email is already registered."
    return True, ""


def verify_student_account(email: str, password: str) -> dict | None:
    """Return account dict if credentials match, else None. Sign-in email must be @uw.edu."""
    em = email.strip().lower()
    if not em or not is_valid_uw_student_email(em):
        return None
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, email, first_name, last_name, password_salt, password_hash
            FROM student_accounts WHERE lower(email) = ?
            """,
            (em,),
        ).fetchone()
    if row is None:
        return None
    if not _verify_teacher_password(
        password, str(row["password_salt"]), str(row["password_hash"])
    ):
        return None
    fn = str(row["first_name"] or "")
    ln = str(row["last_name"] or "")
    return {
        "id": int(row["id"]),
        "email": str(row["email"]),
        "first_name": fn,
        "last_name": ln,
        "display_name": student_roster_display_name(fn, ln),
    }


def change_student_password(
    *, email: str, current_password: str, new_password: str
) -> tuple[bool, str]:
    if len(new_password) < 8:
        return False, "New password must be at least 8 characters."
    acct = verify_student_account(email.strip().lower(), current_password)
    if acct is None:
        return False, "Current password is incorrect."
    salt, pw_hash = _hash_teacher_password(new_password)
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE student_accounts SET password_salt = ?, password_hash = ?
            WHERE id = ?
            """,
            (salt, pw_hash, int(acct["id"])),
        )
    return True, ""


def fetch_student_accounts_summary() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, email, first_name, last_name, created_at
            FROM student_accounts
            ORDER BY email COLLATE NOCASE
            """
        ).fetchall()
    return [dict(r) for r in rows]


def fetch_student_account_by_id(student_id: int) -> dict | None:
    """Profile fields for the signed-in student (no password hash)."""
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, email, first_name, last_name, created_at
            FROM student_accounts WHERE id = ?
            """,
            (int(student_id),),
        ).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["display_name"] = student_roster_display_name(
        str(d.get("first_name") or ""), str(d.get("last_name") or "")
    )
    return d


def update_student_account_names(
    student_id: int, first_name: str, last_name: str
) -> tuple[bool, str]:
    fn = first_name.strip()
    ln = last_name.strip()
    if not fn:
        return False, "First name is required."
    if not ln:
        return False, "Last name is required."
    with get_conn() as conn:
        cur = conn.execute(
            """
            UPDATE student_accounts SET first_name = ?, last_name = ?
            WHERE id = ?
            """,
            (fn, ln, int(student_id)),
        )
        if cur.rowcount == 0:
            return False, "Account not found."
    return True, ""


def register_student_account(
    email: str, password: str, first_name: str, last_name: str
) -> tuple[bool, str]:
    """Self-service signup: UW email, password, legal name. Roster/CFO uses full name when enrolling."""
    em = email.strip().lower()
    fn = first_name.strip()
    ln = last_name.strip()
    if not is_valid_uw_student_email(em):
        return False, f"Use your UW email address (must end with {UW_STUDENT_EMAIL_SUFFIX})."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not fn:
        return False, "First name is required."
    if not ln:
        return False, "Last name is required."
    salt, pw_hash = _hash_teacher_password(password)
    ts = utc_now_iso()
    try:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO student_accounts (
                    email, password_salt, password_hash, first_name, last_name, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (em, salt, pw_hash, fn, ln, ts),
            )
    except sqlite3.IntegrityError:
        return False, "That email is already registered. Sign in or use a different address."
    return True, ""


def fetch_enrollments_for_student(
    student_id: int, *, visible_on_student_dashboard_only: bool = True
) -> list[dict]:
    """Per-class roster identity for this account."""
    vis_clause = ""
    if visible_on_student_dashboard_only:
        vis_clause = " AND COALESCE(visible_on_student_dashboard, 1) = 1 "
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT class_name, cfo_name, team_number, team_name, enrolled_at,
                   COALESCE(visible_on_student_dashboard, 1) AS visible_on_student_dashboard
            FROM student_enrollments
            WHERE student_id = ? {vis_clause}
            ORDER BY class_name COLLATE NOCASE
            """,
            (int(student_id),),
        ).fetchall()
    return [dict(r) for r in rows]


def fetch_enrolled_class_names_for_student(
    student_id: int, *, visible_on_student_dashboard_only: bool = True
) -> list[str]:
    return [
        str(r["class_name"])
        for r in fetch_enrollments_for_student(
            student_id, visible_on_student_dashboard_only=visible_on_student_dashboard_only
        )
    ]


def enrollment_row_for_student_class(student_id: int, class_name: str) -> dict | None:
    """Enrollment for this class regardless of dashboard visibility (e.g. confirm in-flight order)."""
    cn = class_name.strip()
    if not cn:
        return None
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT class_name, cfo_name, team_number, team_name, enrolled_at,
                   COALESCE(visible_on_student_dashboard, 1) AS visible_on_student_dashboard
            FROM student_enrollments
            WHERE student_id = ? AND class_name = ?
            """,
            (int(student_id), cn),
        ).fetchone()
    return dict(row) if row else None


def fetch_enrollments_for_admin_visibility() -> list[dict]:
    """All enrollments with account email and dashboard visibility (admin tooling)."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
              se.student_id AS student_id,
              sa.email AS student_email,
              se.cfo_name AS cfo_name,
              se.team_number AS team_number,
              se.team_name AS team_name,
              se.class_name AS class_name,
              se.enrolled_at AS enrolled_at,
              COALESCE(se.visible_on_student_dashboard, 1) AS visible_on_student_dashboard
            FROM student_enrollments se
            INNER JOIN student_accounts sa ON sa.id = se.student_id
            ORDER BY se.class_name COLLATE NOCASE, sa.email COLLATE NOCASE
            """
        ).fetchall()
    return [dict(r) for r in rows]


def fetch_enrollments_roster_for_class(class_name: str) -> list[dict]:
    """Students enrolled in a class with account email and roster fields (teacher view)."""
    cn = (class_name or "").strip()
    if not cn:
        return []
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
              se.student_id AS student_id,
              sa.email AS email,
              sa.first_name AS first_name,
              sa.last_name AS last_name,
              se.cfo_name AS cfo_name,
              se.team_number AS team_number,
              se.team_name AS team_name,
              se.enrolled_at AS enrolled_at
            FROM student_enrollments se
            INNER JOIN student_accounts sa ON sa.id = se.student_id
            WHERE se.class_name = ?
            ORDER BY sa.email COLLATE NOCASE, se.team_number
            """,
            (cn,),
        ).fetchall()
    return [dict(r) for r in rows]


def set_enrollment_visible_on_student_dashboard(
    student_id: int, class_name: str, *, visible: bool
) -> tuple[bool, str]:
    """When visible is False, the student no longer sees that class on their dashboard; orders remain for admin."""
    cn = class_name.strip()
    if not cn:
        return False, "Class name is required."
    with get_conn() as conn:
        cur = conn.execute(
            """
            UPDATE student_enrollments
            SET visible_on_student_dashboard = ?
            WHERE student_id = ? AND class_name = ?
            """,
            (1 if visible else 0, int(student_id), cn),
        )
        if cur.rowcount == 0:
            return False, "No enrollment found for that student and class."
    return True, ""


def enroll_student_in_class(
    *,
    student_id: int,
    class_name: str,
    team_number: int,
    team_name: str,
    passcode: str | None = None,
) -> tuple[bool, str]:
    """Enroll if the class exists and passcode matches when set. CFO on orders = student's registered full name."""
    tname = team_name.strip()
    cn = class_name.strip()
    if not cn:
        return False, "Pick a class."
    if team_number < 1:
        return False, "Team number must be at least 1."
    if not tname:
        return False, "Team name is required."
    with get_conn() as conn:
        acc = conn.execute(
            "SELECT first_name, last_name FROM student_accounts WHERE id = ?",
            (int(student_id),),
        ).fetchone()
        if not acc:
            return False, "Account not found."
        cfo = student_roster_display_name(str(acc["first_name"] or ""), str(acc["last_name"] or ""))
        if not cfo:
            return False, (
                "Add your first and last name to your profile before enrolling. "
                "Use **Your name** on the dashboard if you see it."
            )
        row = conn.execute(
            "SELECT enroll_passcode FROM teacher_classes WHERE class_name = ?",
            (cn,),
        ).fetchone()
        if not row:
            return False, "That class is no longer available."
        stored = (row["enroll_passcode"] or "").strip()
        sub = (passcode or "").strip()
        if stored and sub != stored:
            return False, "Incorrect enrollment passcode."
        try:
            conn.execute(
                """
                INSERT INTO student_enrollments (
                    student_id, class_name, cfo_name, team_number, team_name,
                    enrolled_at, visible_on_student_dashboard
                )
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    int(student_id),
                    cn,
                    cfo,
                    int(team_number),
                    tname,
                    utc_now_iso(),
                ),
            )
        except sqlite3.IntegrityError:
            return False, "You are already enrolled in that class."
    return True, ""


def fetch_all_teacher_classes() -> list[dict]:
    """All teacher-created classes, ordered by name (student dropdown + budgets)."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, class_name, budget_usd, teacher_name, enroll_passcode,
                   COALESCE(quarter, '') AS quarter
            FROM teacher_classes
            ORDER BY class_name COLLATE NOCASE
            """
        ).fetchall()
        return [dict(r) for r in rows]


def fetch_teacher_classes_for_teacher(teacher_name: str) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, class_name, budget_usd, teacher_name, enroll_passcode,
                   COALESCE(quarter, '') AS quarter
            FROM teacher_classes
            WHERE teacher_name = ?
            ORDER BY class_name COLLATE NOCASE
            """,
            (teacher_name,),
        ).fetchall()
        return [dict(r) for r in rows]


def insert_teacher_class(
    *,
    class_name: str,
    budget_usd: float,
    teacher_name: str,
    enroll_passcode: str,
    quarter: str,
) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO teacher_classes (class_name, budget_usd, teacher_name, enroll_passcode, quarter)
            VALUES (?, ?, ?, ?, ?)
            """,
            (class_name, budget_usd, teacher_name, enroll_passcode.strip(), quarter),
        )
        return int(cur.lastrowid)


def update_teacher_class_budget(
    *, class_name: str, budget_usd: float, teacher_name: str
) -> bool:
    """Update budget only if this teacher owns the class. Returns whether a row was updated."""
    with get_conn() as conn:
        cur = conn.execute(
            """
            UPDATE teacher_classes SET budget_usd = ?
            WHERE class_name = ? AND teacher_name = ?
            """,
            (budget_usd, class_name, teacher_name),
        )
        return cur.rowcount > 0


def delete_teacher_class(*, class_name: str, teacher_name: str) -> bool:
    """Remove a class owned by this teacher, enrollments, orders, and legacy budget row."""
    with get_conn() as conn:
        cur = conn.execute(
            """
            DELETE FROM teacher_classes
            WHERE class_name = ? AND teacher_name = ?
            """,
            (class_name, teacher_name),
        )
        if cur.rowcount == 0:
            return False
        conn.execute(
            "DELETE FROM student_enrollments WHERE class_name = ?",
            (class_name,),
        )
        conn.execute(
            "DELETE FROM orders WHERE class_name = ?",
            (class_name,),
        )
        conn.execute(
            "DELETE FROM class_budgets WHERE class_name = ?",
            (class_name,),
        )
    return True


def get_all_class_budgets() -> dict[str, float]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT class_name, budget_usd FROM class_budgets"
        ).fetchall()
        return {str(r["class_name"]): float(r["budget_usd"]) for r in rows}


def upsert_class_budget(class_name: str, budget_usd: float) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO class_budgets (class_name, budget_usd)
            VALUES (?, ?)
            ON CONFLICT(class_name) DO UPDATE SET budget_usd = excluded.budget_usd
            """,
            (class_name, budget_usd),
        )


def insert_order(
    *,
    class_name: str,
    team_number: int,
    cfo_name: str,
    provider: str,
    item_name: str,
    quantity: float,
    unit_price: float,
    link_url: str,
    notes: str,
    order_group_id: str | None = None,
) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO orders (
                created_at, order_group_id, class_name, team_number, cfo_name, provider,
                item_name, quantity, unit_price, link_url, notes, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """,
            (
                utc_now_iso(),
                order_group_id,
                class_name,
                team_number,
                cfo_name,
                provider,
                item_name,
                quantity,
                unit_price,
                link_url,
                notes,
            ),
        )
        return int(cur.lastrowid)


def insert_orders_group(
    *,
    order_group_id: str,
    class_name: str,
    team_number: int,
    cfo_name: str,
    lines: list[tuple[str, float, float, str, str, str]],
) -> list[int]:
    """Insert multiple line items sharing one order_group_id and one timestamp.

    Each line is (item_name, quantity, unit_price, link_url, notes, provider).
    """
    created_at = utc_now_iso()
    ids: list[int] = []
    with get_conn() as conn:
        for item_name, quantity, unit_price, link_url, notes, provider in lines:
            cur = conn.execute(
                """
                INSERT INTO orders (
                    created_at, order_group_id, class_name, team_number, cfo_name, provider,
                    item_name, quantity, unit_price, link_url, notes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    created_at,
                    order_group_id,
                    class_name,
                    team_number,
                    cfo_name,
                    provider,
                    item_name,
                    quantity,
                    unit_price,
                    link_url,
                    notes,
                ),
            )
            ids.append(int(cur.lastrowid))
    return ids


def fetch_all_orders():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, order_group_id, class_name, team_number, cfo_name, provider,
                   item_name, quantity, unit_price, link_url, notes, status, attention_message,
                   COALESCE(admin_fulfillment, 'ongoing') AS admin_fulfillment
            FROM orders
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]


def fetch_pending_orders_for_classes(class_names: list[str]) -> list[dict]:
    """Pending line items whose class is owned by this teacher's class list."""
    if not class_names:
        return []
    placeholders = ",".join("?" * len(class_names))
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT id, created_at, order_group_id, class_name, team_number, cfo_name, provider,
                   item_name, quantity, unit_price, link_url, notes, status, attention_message,
                   COALESCE(admin_fulfillment, 'ongoing') AS admin_fulfillment
            FROM orders
            WHERE LOWER(status) = 'pending' AND class_name IN ({placeholders})
            ORDER BY created_at ASC, id ASC
            """,
            tuple(class_names),
        ).fetchall()
        return [dict(r) for r in rows]


def fetch_orders_for_classes_by_status(
    class_names: list[str],
    *,
    status: str,
    newest_first: bool = True,
) -> list[dict]:
    """Order lines for the given classes with exact status (case-insensitive), ordered by time."""
    if not class_names:
        return []
    status_lc = (status or "").strip().lower()
    if not status_lc:
        return []
    placeholders = ",".join("?" * len(class_names))
    ord_clause = "DESC" if newest_first else "ASC"
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT id, created_at, order_group_id, class_name, team_number, cfo_name, provider,
                   item_name, quantity, unit_price, link_url, notes, status, attention_message,
                   COALESCE(admin_fulfillment, 'ongoing') AS admin_fulfillment
            FROM orders
            WHERE LOWER(TRIM(status)) = ? AND class_name IN ({placeholders})
            ORDER BY created_at {ord_clause}, id {ord_clause}
            """,
            (status_lc, *tuple(class_names)),
        ).fetchall()
    return [dict(r) for r in rows]


def update_order_status_and_message(
    order_id: int,
    status: str,
    attention_message: str | None = None,
) -> None:
    with get_conn() as conn:
        if attention_message is None:
            conn.execute(
                """
                UPDATE orders SET status = ?, attention_message = NULL WHERE id = ?
                """,
                (status, order_id),
            )
        else:
            conn.execute(
                """
                UPDATE orders SET status = ?, attention_message = ? WHERE id = ?
                """,
                (status, attention_message, order_id),
            )


def update_order_status(order_id: int, status: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id),
        )


def delete_pending_order_line_for_student(order_line_id: int, student_id: int) -> tuple[bool, str]:
    """Remove one line item only if it is still pending and tied to this student's enrollment."""
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, class_name, cfo_name, status
            FROM orders
            WHERE id = ?
            """,
            (int(order_line_id),),
        ).fetchone()
        if row is None:
            return False, "That request was not found."
        if str(row["status"] or "").strip().lower() != "pending":
            return (
                False,
                "You can only remove requests that are still **pending** instructor approval.",
            )
        en = conn.execute(
            """
            SELECT 1 FROM student_enrollments
            WHERE student_id = ? AND class_name = ? AND cfo_name = ?
            """,
            (int(student_id), str(row["class_name"]), str(row["cfo_name"])),
        ).fetchone()
        if en is None:
            return False, "You can only remove requests that belong to your enrollments."
        conn.execute("DELETE FROM orders WHERE id = ?", (int(order_line_id),))
    return True, ""


def update_orders_statuses(updates: list[tuple[int, str]]) -> None:
    with get_conn() as conn:
        conn.executemany(
            "UPDATE orders SET status = ? WHERE id = ?",
            [(status, oid) for oid, status in updates],
        )


def update_orders_admin_fulfillment(updates: list[tuple[int, str]]) -> None:
    """updates: (order_id, admin_fulfillment) with values like 'ongoing' | 'completed'."""
    with get_conn() as conn:
        conn.executemany(
            "UPDATE orders SET admin_fulfillment = ? WHERE id = ?",
            [(fulfillment, oid) for oid, fulfillment in updates],
        )


def fetch_archived_quarter_set() -> set[str]:
    with get_conn() as conn:
        rows = conn.execute("SELECT quarter FROM admin_archived_quarters").fetchall()
        return {str(r["quarter"]) for r in rows}


def set_quarter_archived(quarter: str, *, archived: bool) -> None:
    q = quarter.strip()
    if not q:
        return
    with get_conn() as conn:
        if archived:
            conn.execute(
                "INSERT OR IGNORE INTO admin_archived_quarters (quarter) VALUES (?)",
                (q,),
            )
        else:
            conn.execute(
                "DELETE FROM admin_archived_quarters WHERE quarter = ?",
                (q,),
            )
