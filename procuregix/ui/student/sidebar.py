from __future__ import annotations

import html

import streamlit as st

from procuregix.auth.session import (
    _session_student_display_name,
    _session_student_email,
    _student_clear_session,
)
from procuregix.ui.styles import inject_student_sidebar_nav_styles

STUDENT_NAV_MY_CLASSES = "my_classes"
STUDENT_NAV_ALL_ORDERS = "all_orders"
STUDENT_NAV_NOTIFICATIONS = "notifications"
STUDENT_NAV_ENROLL = "enroll"
STUDENT_NAV_CHANGE_PASSWORD = "change_password"

_STUDENT_NAV_ITEMS: tuple[tuple[str, str], ...] = (
    (STUDENT_NAV_NOTIFICATIONS, "Notifications"),
    (STUDENT_NAV_MY_CLASSES, "My Classes"),
    (STUDENT_NAV_ALL_ORDERS, "All Orders"),
    (STUDENT_NAV_ENROLL, "Enroll in a class"),
    (STUDENT_NAV_CHANGE_PASSWORD, "Change password"),
)


def _student_nav_shell():
    try:
        return st.sidebar.container(border=False, key="pgx_student_nav_tabs")
    except TypeError:
        return st.sidebar.container(border=False)


def render_student_sidebar() -> None:
    """Left sidebar: main areas + log out (mirrors instructor layout)."""
    inject_student_sidebar_nav_styles()
    if "student_menu_choice" not in st.session_state:
        st.session_state.student_menu_choice = STUDENT_NAV_NOTIFICATIONS

    st.sidebar.markdown("##### ProcureGIX")
    st.sidebar.caption("Student account")
    dn = html.escape(_session_student_display_name() or "")
    em = html.escape(_session_student_email() or "")
    if dn:
        st.sidebar.markdown(f"**{dn}**", unsafe_allow_html=True)
    if em:
        st.sidebar.caption(em)
    st.sidebar.divider()

    with _student_nav_shell():
        for nav_id, label in _STUDENT_NAV_ITEMS:
            selected = st.session_state.get("student_menu_choice") == nav_id
            if st.button(
                label,
                key=f"student_nav_btn_{nav_id}",
                type="primary" if selected else "secondary",
                use_container_width=True,
            ):
                st.session_state.student_menu_choice = nav_id
                st.session_state.student_view = "dashboard"
                st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("Log out", type="primary", use_container_width=True, key="student_sidebar_logout"):
        for k in (
            "student_menu_choice",
            "student_view",
            "student_show_enroll_ui",
            "student_show_extra_enroll",
            "student_order_confirm",
            "student_resubmit_order",
            "student_form_preset_class",
            "student_form_warning",
            "student_form_class",
            "item_row_ids",
            "student_pw_current",
            "student_pw_new",
            "student_pw_new2",
        ):
            st.session_state.pop(k, None)
        prefix = "pgx_"
        for k in list(st.session_state.keys()):
            if isinstance(k, str) and k.startswith(prefix):
                del st.session_state[k]
        _student_clear_session()
        st.rerun()
