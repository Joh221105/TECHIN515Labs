from __future__ import annotations

import streamlit as st

from procuregix.ui.styles import inject_admin_sidebar_nav_styles

ADMIN_NAV_ARCHIVE = "archive"
ADMIN_NAV_CLASSES = "classes"
ADMIN_NAV_INSTRUCTOR = "instructor_account"
ADMIN_NAV_ALL_ORDERS = "all_orders"

_ADMIN_NAV_ITEMS: tuple[tuple[str, str], ...] = (
    (ADMIN_NAV_ARCHIVE, "Archive"),
    (ADMIN_NAV_CLASSES, "Classes"),
    (ADMIN_NAV_INSTRUCTOR, "Instructor account"),
    (ADMIN_NAV_ALL_ORDERS, "All orders"),
)


def _admin_nav_shell():
    try:
        return st.sidebar.container(border=False, key="pgx_admin_nav_tabs")
    except TypeError:
        return st.sidebar.container(border=False)


def _normalize_legacy_admin_view() -> None:
    """Map old admin_view flags onto sidebar menu choice."""
    v = st.session_state.get("admin_view")
    if v == "instructor_accounts":
        st.session_state.admin_menu_choice = ADMIN_NAV_INSTRUCTOR
        st.session_state.admin_view = "orders"
    elif v == "student_accounts":
        st.session_state.admin_view = "orders"


def render_admin_sidebar() -> None:
    """Left sidebar: admin areas (same button pattern as student / instructor)."""
    inject_admin_sidebar_nav_styles()
    _normalize_legacy_admin_view()

    if "admin_menu_choice" not in st.session_state:
        st.session_state.admin_menu_choice = ADMIN_NAV_CLASSES
    if st.session_state.get("admin_menu_choice") == "notifications":
        st.session_state.admin_menu_choice = ADMIN_NAV_CLASSES

    st.sidebar.markdown("##### ProcureGIX")
    st.sidebar.caption("Admin account")
    st.sidebar.divider()

    with _admin_nav_shell():
        for nav_id, label in _ADMIN_NAV_ITEMS:
            selected = st.session_state.get("admin_menu_choice") == nav_id
            if st.button(
                label,
                key=f"admin_nav_btn_{nav_id}",
                type="primary" if selected else "secondary",
                use_container_width=True,
            ):
                st.session_state.admin_menu_choice = nav_id
                st.rerun()

    st.sidebar.divider()
