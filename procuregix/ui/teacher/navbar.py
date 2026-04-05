from __future__ import annotations

import streamlit as st

from db import change_teacher_password

from procuregix.auth.session import _session_teacher_username


def render_teacher_change_password_page() -> None:
    """Full-page change password form (teacher sidebar tab)."""
    st.subheader("Change password")
    un = _session_teacher_username()
    if not un:
        st.info(
            "Password change is only available when you sign in with a username and password. "
            "If you use single sign-on, manage your password with your organization."
        )
        return

    st.caption("Use your current password, then choose a new one (at least 8 characters).")
    st.text_input("Current password", type="password", key="teacher_pw_current")
    st.text_input("New password", type="password", key="teacher_pw_new")
    st.text_input("Confirm new password", type="password", key="teacher_pw_new2")
    if st.button("Update password", type="primary", key="teacher_pw_save"):
        cur = str(st.session_state.get("teacher_pw_current") or "")
        n1 = str(st.session_state.get("teacher_pw_new") or "")
        n2 = str(st.session_state.get("teacher_pw_new2") or "")
        if n1 != n2:
            st.error("New passwords do not match.")
        else:
            ok, err = change_teacher_password(
                username=un,
                current_password=cur,
                new_password=n1,
            )
            if ok:
                st.session_state["teacher_class_flash"] = "Password updated."
                st.rerun()
            else:
                st.error(err)
