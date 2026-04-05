from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from db import (
    delete_teacher_class,
    fetch_enrollments_roster_for_class,
    fetch_orders_for_classes_by_status,
    fetch_pending_orders_for_classes,
    fetch_teacher_classes_for_teacher,
    student_roster_display_name,
    update_order_status_and_message,
)

from procuregix.auth.session import (
    _require_teacher_db_identity,
    _teacher_clear_session,
    _teacher_display_name,
)
from procuregix.ui.styles import (
    inject_class_expander_heading_styles,
    inject_teacher_order_action_styles,
    inject_teacher_order_detail_card_styles,
    inject_teacher_sidebar_nav_styles,
)
from procuregix.ui.teacher.add_class import run_teacher_add_class_form
from procuregix.ui.teacher.callbacks import (
    teacher_cancel_delete_class,
    teacher_start_delete_class,
)
from procuregix.ui.teacher.navbar import render_teacher_change_password_page
from procuregix.utils.formatting import stable_key

TEACHER_NAV_ORDERS = "orders"
TEACHER_NAV_CLASSES = "classes"
TEACHER_NAV_PASSWORD = "change_password"

_TEACHER_NAV_ITEMS: tuple[tuple[str, str], ...] = (
    (TEACHER_NAV_ORDERS, "Orders"),
    (TEACHER_NAV_CLASSES, "Classes"),
    (TEACHER_NAV_PASSWORD, "Change password"),
)

_LEGACY_MENU_MAP = {
    "Pending Approvals (Home)": TEACHER_NAV_ORDERS,
    "Pending Approvals": TEACHER_NAV_ORDERS,
    "Classes": TEACHER_NAV_CLASSES,
    "Change password": TEACHER_NAV_PASSWORD,
}


def _normalize_teacher_menu_choice(raw: object) -> str:
    if isinstance(raw, str) and raw in {k for k, _ in _TEACHER_NAV_ITEMS}:
        return raw
    if isinstance(raw, str) and raw in _LEGACY_MENU_MAP:
        return _LEGACY_MENU_MAP[raw]
    return TEACHER_NAV_ORDERS


def _leave_add_class_if_not_classes(nav_id: str) -> None:
    if nav_id != TEACHER_NAV_CLASSES and st.session_state.get("teacher_view") == "add_form":
        st.session_state.teacher_view = "list"


def _teacher_nav_shell():
    try:
        return st.sidebar.container(border=False, key="pgx_teacher_nav_tabs")
    except TypeError:
        return st.sidebar.container(border=False)


def _render_teacher_sidebar() -> None:
    disp = _teacher_display_name() or "Instructor"
    inject_teacher_sidebar_nav_styles()
    st.sidebar.markdown("##### ProcureGIX")
    st.sidebar.caption("Instructor account")
    st.sidebar.markdown(f"**{disp}**")
    st.sidebar.divider()

    if st.session_state.get("teacher_view") == "add_form":
        st.session_state["teacher_menu_choice"] = TEACHER_NAV_CLASSES

    with _teacher_nav_shell():
        for nav_id, label in _TEACHER_NAV_ITEMS:
            selected = st.session_state.get("teacher_menu_choice") == nav_id
            if st.button(
                label,
                key=f"teacher_nav_btn_{nav_id}",
                type="primary" if selected else "secondary",
                use_container_width=True,
            ):
                _leave_add_class_if_not_classes(nav_id)
                st.session_state.teacher_menu_choice = nav_id
                st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("Log out", type="primary", use_container_width=True):
        for k in (
            "teacher_menu_choice",
            "teacher_view",
            "teacher_delete_confirm_class",
            "teacher_rejecting_id",
            "teacher_nav_pw_open",
        ):
            st.session_state.pop(k, None)
        _teacher_clear_session()
        st.rerun()


def _order_line_card_common(row: dict) -> None:
    rid = int(row["id"])
    st.markdown(
        f"**Order #{rid}** · Class **{row['class_name']}** · Team **{row['team_number']}** · "
        f"CFO **{row['cfo_name']}**"
    )
    st.markdown(f"**Item:** {row['item_name']}")
    st.markdown(
        f"**Quantity:** {row['quantity']} · **Price (per unit):** ${float(row['unit_price']):,.2f}"
    )
    link_url = (row.get("link_url") or "").strip()
    if link_url:
        safe_href = html.escape(link_url, quote=True)
        st.markdown(
            f'**Link to purchase:** <a href="{safe_href}" target="_blank" '
            f'rel="noopener noreferrer">Open link</a>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("**Link to purchase:** —")
    st.markdown(f"**Notes:** {row['notes']}")
    prov = (row.get("provider") or "").strip()
    if prov:
        st.caption(f"Provider: {prov}")


def _order_detail_card_body(row: dict) -> None:
    """Pending / Approved detail cards: provider as markdown line (matches scaled body text)."""
    rid = int(row["id"])
    st.markdown(
        f"**Order #{rid}** · **Class** {row['class_name']} · **Team** {row['team_number']} · "
        f"**CFO** {row['cfo_name']}"
    )
    st.markdown(f"**Item:** {row['item_name']}")
    st.markdown(
        f"**Quantity:** {row['quantity']} · **Price (per unit):** ${float(row['unit_price']):,.2f}"
    )
    link_url = (row.get("link_url") or "").strip()
    if link_url:
        safe_href = html.escape(link_url, quote=True)
        st.markdown(
            f'**Link to purchase:** <a href="{safe_href}" target="_blank" '
            f'rel="noopener noreferrer">Open link</a>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("**Link to purchase:** —")
    st.markdown(f"**Notes:** {row['notes']}")
    prov = (row.get("provider") or "").strip()
    if prov:
        st.markdown(f"**Provider:** {prov}")


def _order_action_shell(key: str):
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def _render_pending_order_action_buttons(row: dict) -> None:
    """Approve / Reject stacked in the narrow side column."""
    rid = int(row["id"])
    with _order_action_shell(f"pgx_ord_appr_{rid}"):
        if st.button("Approve", type="primary", key=f"ta_appr_{rid}", use_container_width=True):
            update_order_status_and_message(rid, "approved")
            st.rerun()
    with _order_action_shell(f"pgx_ord_rej_{rid}"):
        if st.button("Reject", type="primary", key=f"ta_reject_{rid}", use_container_width=True):
            st.session_state.teacher_rejecting_id = rid
            st.rerun()


def _render_pending_order_reject_flow(row: dict) -> None:
    rid = int(row["id"])
    st.text_area(
        "Feedback for student (required)",
        key=f"teacher_reject_fb_{rid}",
        height=100,
        max_chars=2000,
        placeholder="Explain what needs to change so they can resubmit.",
    )
    c_cf, c_cc = st.columns(2)
    with c_cf:
        with _order_action_shell(f"pgx_ord_confirm_rej_{rid}"):
            if st.button("Confirm rejection", type="primary", key=f"ta_confirm_rej_{rid}"):
                fb = (st.session_state.get(f"teacher_reject_fb_{rid}") or "").strip()
                if not fb:
                    st.error("Please enter feedback before confirming.")
                else:
                    update_order_status_and_message(rid, "rejected", fb)
                    st.session_state.teacher_rejecting_id = None
                    st.rerun()
    with c_cc:
        with _order_action_shell(f"pgx_ord_cancel_rej_{rid}"):
            if st.button("Cancel", key=f"ta_cancel_rej_{rid}"):
                st.session_state.teacher_rejecting_id = None
                st.rerun()


def _approved_order_side_column(row: dict) -> None:
    """Right column on Approved cards: status and admin fulfillment."""
    st.markdown(f"**Status:** {row.get('status') or 'approved'}")
    ful = str(row.get("admin_fulfillment") or "ongoing").strip() or "ongoing"
    st.markdown(f"**Admin fulfillment:** {ful}")


def _render_pending_approvals(teacher_name: str, *, filter_classes: set[str] | None) -> None:
    inject_teacher_order_detail_card_styles()
    st.caption(
        "Line items awaiting your decision. **Approve** sends them forward; **Reject** requires written feedback."
    )
    my_classes = fetch_teacher_classes_for_teacher(teacher_name)
    my_class_names = [c["class_name"] for c in my_classes]
    pending_rows = fetch_pending_orders_for_classes(my_class_names)
    if filter_classes:
        pending_rows = [r for r in pending_rows if r.get("class_name") in filter_classes]

    if not pending_rows:
        st.info(
            "No pending orders for the selected classes right now."
            if filter_classes
            else "No pending orders for your classes right now."
        )
        return

    for row in pending_rows:
        rid = int(row["id"])
        rejecting_id = st.session_state.get("teacher_rejecting_id")
        try:
            box = st.container(border=True)
        except TypeError:
            box = st.container()
        with box:
            try:
                keyed = st.container(key=f"pgx_pending_card_{rid}")
            except TypeError:
                keyed = st.container()
            with keyed:
                if rejecting_id == rid:
                    _order_detail_card_body(row)
                    _render_pending_order_reject_flow(row)
                else:
                    try:
                        c_main, c_act = st.columns([3.1, 1], gap="large")
                    except TypeError:
                        c_main, c_act = st.columns([3.1, 1])
                    with c_main:
                        _order_detail_card_body(row)
                    with c_act:
                        _render_pending_order_action_buttons(row)


def _render_orders_history(
    teacher_name: str,
    *,
    status: str,
    empty_msg: str,
    detail_horizontal: bool = False,
    filter_classes: set[str] | None,
) -> None:
    my_classes = fetch_teacher_classes_for_teacher(teacher_name)
    my_class_names = [c["class_name"] for c in my_classes]
    rows = fetch_orders_for_classes_by_status(my_class_names, status=status, newest_first=True)
    if filter_classes:
        rows = [r for r in rows if r.get("class_name") in filter_classes]
    if not rows:
        st.info(
            (
                "No rejected orders for the selected classes."
                if status == "rejected"
                else "No approved orders for the selected classes yet."
            )
            if filter_classes
            else empty_msg
        )
        return
    if detail_horizontal:
        inject_teacher_order_detail_card_styles()
    for row in rows:
        rid = int(row["id"])
        try:
            box = st.container(border=True)
        except TypeError:
            box = st.container()
        with box:
            if detail_horizontal:
                try:
                    keyed = st.container(key=f"pgx_approved_card_{rid}")
                except TypeError:
                    keyed = st.container()
                with keyed:
                    try:
                        c_main, c_side = st.columns([3.1, 1], gap="large")
                    except TypeError:
                        c_main, c_side = st.columns([3.1, 1])
                    with c_main:
                        _order_detail_card_body(row)
                    with c_side:
                        _approved_order_side_column(row)
            else:
                _order_line_card_common(row)
                st.markdown(f"**Status:** {row.get('status') or status}")
                if status == "rejected":
                    msg = (row.get("attention_message") or "").strip()
                    if msg:
                        st.markdown(f"**Your feedback to student:** {msg}")


def _render_orders_page(teacher_name: str) -> None:
    inject_teacher_order_action_styles()
    st.subheader("Orders")
    my_class_names = sorted(
        str(c["class_name"]) for c in fetch_teacher_classes_for_teacher(teacher_name)
    )

    tab_pending, tab_rejected, tab_approved = st.tabs(["Pending", "Rejected", "Approved"])
    with tab_pending:
        if not my_class_names:
            st.info("You have no classes yet. Create one under **Classes** to receive orders.")
        else:
            sel = st.multiselect(
                "Filter by Class",
                options=my_class_names,
                default=[],
                key="teacher_orders_filter_pending",
            )
            fc = set(sel) if sel else None
            _render_pending_approvals(teacher_name, filter_classes=fc)
    with tab_rejected:
        if not my_class_names:
            st.info("You have no classes yet. Create one under **Classes** to receive orders.")
        else:
            sel = st.multiselect(
                "Filter by Class",
                options=my_class_names,
                default=[],
                key="teacher_orders_filter_rejected",
            )
            fc = set(sel) if sel else None
            _render_orders_history(
                teacher_name,
                status="rejected",
                empty_msg="No rejected orders for your classes.",
                filter_classes=fc,
            )
    with tab_approved:
        if not my_class_names:
            st.info("You have no classes yet. Create one under **Classes** to receive orders.")
        else:
            sel = st.multiselect(
                "Filter by Class",
                options=my_class_names,
                default=[],
                key="teacher_orders_filter_approved",
            )
            fc = set(sel) if sel else None
            _render_orders_history(
                teacher_name,
                status="approved",
                empty_msg="No approved orders for your classes yet.",
                detail_horizontal=True,
                filter_classes=fc,
            )


def _render_classes(teacher_name: str) -> None:
    st.subheader("Classes")
    st.caption("Enrollment passcodes, registered students, and class actions.")

    head_l, head_r = st.columns([3, 1])
    with head_l:
        st.markdown("##### My classes")
    with head_r:
        if st.button("Add New Class", type="primary", use_container_width=True):
            st.session_state.teacher_view = "add_form"
            st.session_state["teacher_menu_choice"] = TEACHER_NAV_CLASSES
            st.rerun()

    my_classes = fetch_teacher_classes_for_teacher(teacher_name)

    if not my_classes:
        st.info("You have not created any classes yet. Use **Add New Class** to create one.")
        return

    inject_class_expander_heading_styles()
    for i, c in enumerate(my_classes):
        cn = c["class_name"]
        slug = stable_key(cn, "tc")

        q = (c.get("quarter") or "").strip()
        title = f"{cn} — {q}" if q else f"{cn} (no quarter assigned)"
        with st.expander(title, expanded=(i == 0)):
            ep = (c.get("enroll_passcode") or "").strip()
            if ep:
                show_pc = st.checkbox(
                    "Show enrollment passcode",
                    key=f"{slug}_show_enroll_pc",
                    value=False,
                    help="When off, the passcode is hidden on screen.",
                )
                disp = ep if show_pc else ("•" * len(ep) if ep else "")
                st.caption(
                    f"Student enrollment passcode: **{disp}** (share only with your class)."
                )
            else:
                st.caption(
                    "No enrollment passcode on file — students can join without one (legacy class)."
                )

            roster = fetch_enrollments_roster_for_class(cn)
            n_roster = len(roster) if roster else 0
            # Streamlit does not allow expanders inside expanders; use a checkbox to show/hide the roster.
            if st.checkbox(
                f"Registered students ({n_roster})",
                value=False,
                key=f"{slug}_roster_toggle",
                help="Open to view the enrollment table for this class.",
            ):
                if roster:
                    rrows = []
                    for r in roster:
                        rrows.append(
                            {
                                "Email": r.get("email") or "",
                                "Name": student_roster_display_name(
                                    str(r.get("first_name") or ""),
                                    str(r.get("last_name") or ""),
                                ),
                                "CFO (orders)": r.get("cfo_name") or "",
                                "Team": r.get("team_number"),
                                "Team name": r.get("team_name") or "",
                                "Enrolled": r.get("enrolled_at") or "",
                            }
                        )
                    st.dataframe(pd.DataFrame(rrows), use_container_width=True, hide_index=True)
                else:
                    st.caption("No students enrolled yet.")

            st.button(
                "Delete class",
                use_container_width=True,
                key=f"{slug}_delete",
                on_click=teacher_start_delete_class,
                args=(cn,),
            )

            if st.session_state.get("teacher_delete_confirm_class") == cn:
                try:
                    dbox = st.container(border=True)
                except TypeError:
                    dbox = st.container()
                with dbox:
                    st.warning(
                        f"Delete **{cn}**? This removes the class, all student enrollments, and "
                        "**all order lines** for this class. You cannot undo this."
                    )
                    d1, d2 = st.columns(2)
                    with d1:
                        if st.button(
                            "Yes, delete this class",
                            type="primary",
                            key=f"{slug}_del_confirm",
                        ):
                            if delete_teacher_class(class_name=cn, teacher_name=teacher_name):
                                st.session_state.teacher_delete_confirm_class = None
                                st.session_state["teacher_class_flash"] = (
                                    f"Deleted **{cn}** and its enrollments and orders."
                                )
                                st.rerun()
                            else:
                                st.error("Could not delete this class.")
                    with d2:
                        st.button(
                            "Cancel",
                            key=f"{slug}_del_cancel",
                            on_click=teacher_cancel_delete_class,
                        )


def run_teacher_dashboard() -> None:
    teacher_name = _require_teacher_db_identity()

    if "teacher_menu_choice" not in st.session_state:
        st.session_state.teacher_menu_choice = TEACHER_NAV_ORDERS
    else:
        st.session_state.teacher_menu_choice = _normalize_teacher_menu_choice(
            st.session_state.teacher_menu_choice
        )

    _render_teacher_sidebar()

    flash = st.session_state.pop("teacher_class_flash", None)
    if flash:
        st.success(flash)

    if st.session_state.get("teacher_view") == "add_form":
        run_teacher_add_class_form()
        return

    page = st.session_state.get("teacher_menu_choice", TEACHER_NAV_ORDERS)
    if page == TEACHER_NAV_ORDERS:
        _render_orders_page(teacher_name)
    elif page == TEACHER_NAV_CLASSES:
        _render_classes(teacher_name)
    else:
        render_teacher_change_password_page()
