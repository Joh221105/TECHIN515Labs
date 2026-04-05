from __future__ import annotations

import streamlit as st


def _st_user_is_logged_in() -> bool:
    """True when OIDC session is active; false if auth is not configured (avoids AttributeError on `st.user`)."""
    try:
        return bool(st.user["is_logged_in"])
    except (KeyError, TypeError):
        return False


def _session_teacher_username() -> str | None:
    raw = st.session_state.get("teacher_auth_username")
    if raw is None:
        return None
    s = str(raw).strip().lower()
    return s or None


def _session_teacher_display() -> str | None:
    raw = st.session_state.get("teacher_auth_display_name")
    if raw is None:
        return None
    s = str(raw).strip()
    return s or None


def _teacher_set_session(*, username: str, display_name: str) -> None:
    st.session_state["teacher_auth_username"] = username.strip().lower()
    st.session_state["teacher_auth_display_name"] = display_name.strip()


def _teacher_clear_session() -> None:
    st.session_state.pop("teacher_auth_username", None)
    st.session_state.pop("teacher_auth_display_name", None)


def _dev_teacher_identity() -> str | None:
    try:
        dev = st.secrets.get("teacher_dev_display_name")
        if dev is not None and str(dev).strip():
            return str(dev).strip()
    except (FileNotFoundError, RuntimeError, TypeError):
        pass
    return None


def _teacher_db_identity() -> str | None:
    """Stable key for `teacher_classes.teacher_name` (app: lowercased username; OIDC/dev: as resolved)."""
    if u := _session_teacher_username():
        return u
    if _st_user_is_logged_in():
        info = dict(st.user)
        em = info.get("email")
        if isinstance(em, str) and em.strip():
            return em.strip().lower()
        for key in ("preferred_username", "sub", "name"):
            val = info.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        return None
    return _dev_teacher_identity()


def _teacher_display_name() -> str | None:
    """Label for header and UI (friendly name when available)."""
    if d := _session_teacher_display():
        return d
    if _st_user_is_logged_in():
        info = dict(st.user)
        for key in ("name", "email", "preferred_username"):
            val = info.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        return None
    return _dev_teacher_identity()


def _teacher_is_authenticated() -> bool:
    return _teacher_db_identity() is not None


def _require_teacher_db_identity() -> str:
    key = _teacher_db_identity()
    if key:
        return key
    st.error("Your instructor session is missing. Please sign in again.")
    st.stop()


def _session_student_email() -> str | None:
    raw = st.session_state.get("student_auth_email")
    if raw is None:
        return None
    s = str(raw).strip().lower()
    return s or None


def _session_student_display_name() -> str | None:
    raw = st.session_state.get("student_display_name")
    if raw is None:
        return None
    s = str(raw).strip()
    return s or None


def _session_student_account_id() -> int | None:
    raw = st.session_state.get("student_account_id")
    if raw is None:
        return None
    try:
        i = int(raw)
    except (TypeError, ValueError):
        return None
    return i if i > 0 else None


def _student_is_authenticated() -> bool:
    return _session_student_account_id() is not None


def _student_set_session_from_account(acct: dict) -> None:
    st.session_state["student_auth_email"] = str(acct["email"]).strip().lower()
    st.session_state["student_account_id"] = int(acct["id"])
    dn = (acct.get("display_name") or "").strip()
    st.session_state["student_display_name"] = dn


def _student_clear_session() -> None:
    for k in (
        "student_auth_email",
        "student_account_id",
        "student_display_name",
        "student_identity_cfo",
        "student_identity_team_number",
        "student_identity_team_name",
    ):
        st.session_state.pop(k, None)


def _require_student_login() -> None:
    if not _student_is_authenticated():
        st.error("Please sign in to continue.")
        st.stop()

