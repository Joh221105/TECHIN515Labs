from __future__ import annotations

import streamlit as st

from db import verify_teacher_account

from procuregix.auth.session import _teacher_set_session


def run_teacher_auth_screen() -> None:
    _, center, _ = st.columns([1, 2, 1])
    with center:
        try:
            panel = st.container(border=True)
        except TypeError:
            panel = st.container()
        with panel:
            st.subheader("Instructor sign-in")
            st.text_input("Email", key="teacher_login_email")
            st.text_input("Password", type="password", key="teacher_login_password")
            if st.button("Log in", type="primary", use_container_width=True, key="teacher_login_submit"):
                un = (st.session_state.get("teacher_login_email") or "").strip().lower()
                pw = str(st.session_state.get("teacher_login_password") or "")
                acct = verify_teacher_account(un, pw)
                if acct:
                    _teacher_set_session(
                        username=acct["username"],
                        display_name=acct["display_name"],
                    )
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
