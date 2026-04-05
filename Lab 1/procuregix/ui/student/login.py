from __future__ import annotations

import streamlit as st

from db import register_student_account, verify_student_account

from procuregix.auth.session import _student_set_session_from_account


def run_student_login_screen() -> None:
    _, center, _ = st.columns([1, 2, 1])
    with center:
        try:
            panel = st.container(border=True)
        except TypeError:
            panel = st.container()
        with panel:
            tab_in, tab_reg = st.tabs(["Sign in", "Create account"])
            with tab_in:
                st.subheader("Student sign-in")
                st.text_input("UW email", key="student_login_email")
                st.text_input("Password", type="password", key="student_login_password")
                if st.button(
                    "Log in", type="primary", use_container_width=True, key="student_login_submit"
                ):
                    em = (st.session_state.get("student_login_email") or "").strip().lower()
                    pw = str(st.session_state.get("student_login_password") or "")
                    acct = verify_student_account(em, pw)
                    if acct:
                        _student_set_session_from_account(acct)
                        st.rerun()
                    else:
                        st.error(
                            "Invalid email or password, or the address is not an @uw.edu account."
                        )
            with tab_reg:
                st.subheader("Create your student account")
                st.text_input("First name", key="student_register_first")
                st.text_input("Last name", key="student_register_last")
                st.text_input("UW email", key="student_register_email")
                st.text_input("Password (min. 8 characters)", type="password", key="student_register_pw")
                st.text_input(
                    "Confirm password", type="password", key="student_register_pw2"
                )
                if st.button(
                    "Create account",
                    type="primary",
                    use_container_width=True,
                    key="student_register_submit",
                ):
                    em = str(st.session_state.get("student_register_email") or "")
                    p1 = str(st.session_state.get("student_register_pw") or "")
                    p2 = str(st.session_state.get("student_register_pw2") or "")
                    fn = str(st.session_state.get("student_register_first") or "")
                    ln = str(st.session_state.get("student_register_last") or "")
                    if p1 != p2:
                        st.error("Passwords do not match.")
                    else:
                        ok, err_msg = register_student_account(em, p1, fn, ln)
                        if ok:
                            acct = verify_student_account(em.strip().lower(), p1)
                            if acct:
                                _student_set_session_from_account(acct)
                                st.session_state["student_order_flash"] = (
                                    "Welcome — open Enroll in a class in the sidebar to join a course."
                                )
                                st.rerun()
                            st.error("Account was created but sign-in failed. Try logging in manually.")
                        else:
                            st.error(err_msg)
