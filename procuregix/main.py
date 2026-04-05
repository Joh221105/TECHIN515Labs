"""
Streamlit app designed to coordinate purchase requests between students and program administrators

Student Dashboard: Students register with their name, enroll per class (team for that course; orders use their registered full name), submit requests, and monitor class budgets

Teacher/Admin Dashboard: Admins provision instructor logins; **students self-register** with **@uw.edu** email. Teachers set per-class budgets when they create classes, then manage approvals; admins get a master orders view and CSV export.

Relational Management: Connects specific team numbers and providers to teacher-defined class budgets, ensuring spending is categorized and tracked.
"""

from __future__ import annotations

import streamlit as st

from db import init_db

from procuregix.auth.session import (
    _student_is_authenticated,
    _teacher_is_authenticated,
)
from procuregix.ui.admin.dashboard import run_admin_dashboard
from procuregix.ui.admin.sidebar import render_admin_sidebar
from procuregix.ui.student import (
    run_student_dashboard,
    run_student_form,
    run_student_login_screen,
)
from procuregix.ui.student.sidebar import render_student_sidebar
from procuregix.ui.teacher import (
    run_teacher_auth_screen,
    run_teacher_dashboard,
)


def main() -> None:
    init_db()

    head_l, head_mid = st.columns([1.45, 4.35])
    with head_l:
        st.title("UW MSTI")
    with head_mid:
        role = st.radio("Role", ["Student", "Teacher", "Admin"], horizontal=True, key="app_role")
    st.divider()

    if role == "Student":
        if not _student_is_authenticated():
            run_student_login_screen()
        else:
            if "student_view" not in st.session_state:
                st.session_state.student_view = "dashboard"
            render_student_sidebar()
            if st.session_state.student_view == "form":
                run_student_form()
            else:
                run_student_dashboard()
    elif role == "Teacher":
        if not _teacher_is_authenticated():
            run_teacher_auth_screen()
        else:
            if "teacher_view" not in st.session_state:
                st.session_state.teacher_view = "list"
            run_teacher_dashboard()
    else:
        render_admin_sidebar()
        run_admin_dashboard()


if __name__ == "__main__":
    main()
