from __future__ import annotations

import pandas as pd
import streamlit as st

from db import admin_create_teacher_account, fetch_teacher_accounts_summary


def run_admin_instructor_accounts_form() -> None:
    st.subheader("Instructor accounts")
    st.caption(
        "Create an **instructor email** and **initial password** for each professor (and a display name for the app header). "
        "Emails are stored in lowercase and used to sign in. Instructors choose **Teacher** in the app; they can change "
        "their password after logging in. Class budgets are set by instructors when they create a class."
    )
    existing = fetch_teacher_accounts_summary()
    if existing:
        st.markdown("##### Existing accounts")
        view = pd.DataFrame(
            [
                {
                    "Instructor's email": r["username"],
                    "Display name": r["display_name"],
                    "Created": r["created_at"],
                }
                for r in existing
            ]
        )
        st.dataframe(view, use_container_width=True, hide_index=True)
    else:
        st.info("No instructor accounts yet. Use the form below to add one.")

    st.markdown("##### New account")
    st.text_input("Instructor's email", key="admin_teacher_email")
    st.text_input("Display name", key="admin_teacher_display")
    st.text_input("Initial password (min. 8 characters)", type="password", key="admin_teacher_password")
    if st.button("Create instructor account", type="primary", key="admin_teacher_create"):
        ok, err_msg = admin_create_teacher_account(
            str(st.session_state.get("admin_teacher_email") or ""),
            str(st.session_state.get("admin_teacher_password") or ""),
            str(st.session_state.get("admin_teacher_display") or ""),
        )
        if ok:
            st.success(
                "Instructor account created. Share their email and initial password with them through a secure channel."
            )
            st.rerun()
        else:
            st.error(err_msg)
