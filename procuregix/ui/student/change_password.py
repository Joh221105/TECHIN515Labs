from __future__ import annotations

import streamlit as st

from db import change_student_password

from procuregix.auth.session import _session_student_email


def render_student_change_password_page() -> None:
    """Full-page change password form (student sidebar tab)."""
    st.subheader("Change password")
    em = _session_student_email()
    if not em:
        st.info("Sign in again to change your password.")
        return

    st.caption("Use your current password, then choose a new one (at least 8 characters).")
    st.text_input("Current password", type="password", key="student_pw_current")
    st.text_input("New password", type="password", key="student_pw_new")
    st.text_input("Confirm new password", type="password", key="student_pw_new2")
    if st.button("Update password", type="primary", key="student_pw_save"):
        cur = str(st.session_state.get("student_pw_current") or "")
        n1 = str(st.session_state.get("student_pw_new") or "")
        n2 = str(st.session_state.get("student_pw_new2") or "")
        if n1 != n2:
            st.error("New passwords do not match.")
        else:
            ok, err = change_student_password(
                email=em,
                current_password=cur,
                new_password=n1,
            )
            if ok:
                st.session_state["student_account_flash"] = "Password updated."
                st.rerun()
            else:
                st.error(err)
