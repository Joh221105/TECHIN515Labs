from __future__ import annotations

import html
import pandas as pd
import streamlit as st

from db import (
    enroll_student_in_class,
    fetch_all_orders,
    fetch_all_teacher_classes,
    fetch_enrollments_for_student,
    fetch_student_account_by_id,
    student_roster_display_name,
    update_student_account_names,
)

from procuregix.auth.session import _require_student_login, _session_student_account_id
from procuregix.ui.components.student_orders import (
    render_student_orders_all_classes,
    render_student_orders_for_class,
)
from procuregix.ui.styles import inject_class_expander_heading_styles
from procuregix.ui.student.actions import open_student_order_form, start_resubmit
from procuregix.ui.student.change_password import render_student_change_password_page
from procuregix.ui.student.sidebar import (
    STUDENT_NAV_ALL_ORDERS,
    STUDENT_NAV_CHANGE_PASSWORD,
    STUDENT_NAV_ENROLL,
    STUDENT_NAV_MY_CLASSES,
    STUDENT_NAV_NOTIFICATIONS,
)
from procuregix.utils.budget import approved_spend_by_class_for_cfo
from procuregix.utils.formatting import (
    notification_body_for_student,
    student_orders_for_notifications,
    student_status_label,
    stable_key,
)


def _render_enrollment_error_full_width(message: str) -> None:
    """Show passcode / enrollment errors at full main-column width (not inside button columns)."""
    t = html.escape((message or "").strip() or "Something went wrong.")
    st.markdown(
        f'<div class="pgx-enroll-error" style="'
        f"width:100%;box-sizing:border-box;background:#ffebee;border:1px solid #e53935;"
        f"border-radius:0.5rem;padding:0.9rem 1.1rem;color:#b71c1c;font-size:1rem;"
        f'line-height:1.45;margin:0.75rem 0 0 0;">'
        f"<strong>Could not enroll</strong><br/>"
        f'<span style="display:block;margin-top:0.35rem;">{t}</span></div>',
        unsafe_allow_html=True,
    )


def _render_first_time_enrollment_form(
    sid: int,
    profile: dict,
    teacher_class_rows: list,
) -> None:
    available = [r["class_name"] for r in teacher_class_rows]
    if not available:
        st.warning("There are no classes to join yet. Ask a teacher to create one first.")
        return
    st.selectbox("Select a class to join", available, key="student_enroll_class_pick")
    st.caption(f"Orders will show your name as **{profile['display_name']}** (from your account).")
    st.number_input("Team number", min_value=1, step=1, value=1, key="student_enroll_team_n")
    st.text_input("Team name (for this class)", key="student_enroll_team_name")
    st.text_input(
        "Enrollment passcode",
        type="password",
        key="student_enroll_passcode",
        help="Your instructor shares this code so only your class can enroll.",
    )
    enroll_err: str | None = None
    ec1, ec2 = st.columns(2)
    with ec1:
        if st.button("Enroll", type="primary", key="student_enroll_confirm"):
            pick = st.session_state.get("student_enroll_class_pick")
            pc = (st.session_state.get("student_enroll_passcode") or "").strip()
            ok, err = enroll_student_in_class(
                student_id=sid,
                class_name=str(pick or ""),
                team_number=int(st.session_state.get("student_enroll_team_n") or 1),
                team_name=str(st.session_state.get("student_enroll_team_name") or ""),
                passcode=pc,
            )
            if ok:
                st.session_state["student_enrollment_flash"] = f"Enrolled in **{pick}**."
                st.session_state.student_menu_choice = STUDENT_NAV_MY_CLASSES
                st.rerun()
            else:
                enroll_err = err
    with ec2:
        if st.button("Clear form", key="student_enroll_cancel"):
            st.session_state["student_enroll_passcode"] = ""
            st.rerun()
    if enroll_err:
        _render_enrollment_error_full_width(enroll_err)


def _render_extra_enroll_panel(
    sid: int,
    profile: dict,
    teacher_class_rows: list,
) -> None:
    st.caption(
        f"Add another course: pick the class, set your team for that course, then enter the passcode. "
        f"Your name on orders stays **{profile['display_name']}**."
    )
    all_class_names = [r["class_name"] for r in teacher_class_rows]
    if not all_class_names:
        st.warning("No classes exist yet.")
        return
    st.selectbox("Class", all_class_names, key="student_extra_enroll_class")
    st.number_input(
        "Team number",
        min_value=1,
        step=1,
        value=1,
        key="student_extra_enroll_team_n",
    )
    st.text_input("Team name (for this class)", key="student_extra_enroll_team_name")
    st.text_input("Enrollment passcode", type="password", key="student_extra_enroll_passcode")
    extra_enroll_err: str | None = None
    if st.button("Enroll", type="primary", use_container_width=True, key="student_extra_enroll_go"):
        pick_x = st.session_state.get("student_extra_enroll_class")
        pc_x = (st.session_state.get("student_extra_enroll_passcode") or "").strip()
        ok, err = enroll_student_in_class(
            student_id=sid,
            class_name=str(pick_x or ""),
            team_number=int(st.session_state.get("student_extra_enroll_team_n") or 1),
            team_name=str(st.session_state.get("student_extra_enroll_team_name") or ""),
            passcode=pc_x,
        )
        if ok:
            st.session_state["student_enrollment_flash"] = f"Enrolled in **{pick_x}**."
            st.session_state.student_menu_choice = STUDENT_NAV_MY_CLASSES
            st.rerun()
        else:
            extra_enroll_err = err
    if extra_enroll_err:
        _render_enrollment_error_full_width(extra_enroll_err)


def _render_notifications_panel(mine: pd.DataFrame) -> None:
    notify_df = student_orders_for_notifications(mine)

    if notify_df.empty:
        st.caption("No items need your attention right now.")
        return
    try:
        nbox = st.container(border=True)
    except TypeError:
        nbox = st.container()
    with nbox:
        notify_rows = list(notify_df.iterrows())
        for j, (_, nr) in enumerate(notify_rows):
            od = nr.to_dict()
            oid = int(od["id"])
            cn = str(od.get("class_name", ""))
            st.markdown(
                f"**{od.get('item_name', '')}** · *{cn}* · **{student_status_label(str(od.get('status', '')))}**"
            )
            st.caption(notification_body_for_student(od))
            if str(od.get("status", "")).lower() == "rejected":
                st.button(
                    "Resubmit",
                    key=f"student_notify_resubmit_{oid}",
                    on_click=start_resubmit,
                    args=(oid,),
                )
            if j < len(notify_rows) - 1:
                st.divider()


def run_student_dashboard() -> None:
    _require_student_login()
    sid = _session_student_account_id()
    assert sid is not None

    flash = st.session_state.pop("student_order_flash", None)
    if flash:
        st.success(flash)
    en_flash = st.session_state.pop("student_enrollment_flash", None)
    if en_flash:
        st.success(en_flash)
    acct_flash = st.session_state.pop("student_account_flash", None)
    if acct_flash:
        st.success(acct_flash)

    profile = fetch_student_account_by_id(sid)
    if profile is None:
        st.error("Could not load your account. Please sign in again.")
        st.stop()

    menu_choice = str(st.session_state.get("student_menu_choice") or STUDENT_NAV_NOTIFICATIONS)
    if menu_choice == STUDENT_NAV_CHANGE_PASSWORD:
        render_student_change_password_page()
        return

    if profile.get("display_name"):
        st.session_state["student_display_name"] = profile["display_name"]
    if not profile.get("display_name"):
        st.text_input("First name", key="student_profile_first")
        st.text_input("Last name", key="student_profile_last")
        if st.button("Save name", type="primary", key="student_profile_save"):
            ok, msg = update_student_account_names(
                sid,
                str(st.session_state.get("student_profile_first") or ""),
                str(st.session_state.get("student_profile_last") or ""),
            )
            if ok:
                fn = str(st.session_state.get("student_profile_first") or "").strip()
                ln = str(st.session_state.get("student_profile_last") or "").strip()
                st.session_state["student_display_name"] = student_roster_display_name(fn, ln)
                st.success("Saved. Use the sidebar to open **Enroll in a class** when you’re ready.")
                st.rerun()
            else:
                st.error(msg)
        st.stop()

    rows = fetch_all_orders()
    df = pd.DataFrame(rows) if rows else pd.DataFrame()

    enrollments_vis = fetch_enrollments_for_student(
        sid, visible_on_student_dashboard_only=True
    )
    enrollments_any = fetch_enrollments_for_student(
        sid, visible_on_student_dashboard_only=False
    )
    enrolled_names = [str(e["class_name"]) for e in enrollments_vis]
    enrolled_any_names = [str(e["class_name"]) for e in enrollments_any]
    enroll_by_class = {str(e["class_name"]): e for e in enrollments_vis}
    visible_pairs = {(str(e["class_name"]), str(e["cfo_name"])) for e in enrollments_vis}

    mine_all = (
        df[
            df.apply(
                lambda r: (str(r["class_name"]), str(r["cfo_name"])) in visible_pairs,
                axis=1,
            )
        ].copy()
        if not df.empty and visible_pairs
        else pd.DataFrame()
    )
    mine = mine_all

    teacher_class_rows = fetch_all_teacher_classes()
    all_teacher_names = {r["class_name"] for r in teacher_class_rows}
    budgets_map = {r["class_name"]: float(r["budget_usd"]) for r in teacher_class_rows}
    quarter_map = {
        r["class_name"]: (r.get("quarter") or "").strip() for r in teacher_class_rows
    }

    menu = str(st.session_state.get("student_menu_choice") or STUDENT_NAV_NOTIFICATIONS)

    if not enrolled_names:
        if menu == STUDENT_NAV_MY_CLASSES:
            if enrolled_any_names:
                st.info(
                    "**No classes are shown on your dashboard right now.** "
                    "An administrator may have hidden past classes after the term ended. "
                    "Your submissions still exist for program records. "
                    "If this looks wrong, contact your instructor or administrator."
                )
            else:
                st.info("**You aren’t enrolled in any classes yet.**")
            st.caption("Use **Enroll in a class** in the sidebar to join with your team and passcode.")
        elif menu == STUDENT_NAV_ENROLL:
            st.subheader("Enroll in a class")
            _render_first_time_enrollment_form(sid, profile, teacher_class_rows)
            if enrolled_any_names and not enrolled_names:
                st.caption(
                    "You can still join a new class here. Hidden past classes stay off **My Classes**."
                )
        elif menu == STUDENT_NAV_ALL_ORDERS:
            st.subheader("All orders")
            st.caption("After you enroll, your submitted lines will appear here.")
        elif menu == STUDENT_NAV_NOTIFICATIONS:
            st.caption("Alerts for rejected lines and other items show up here once you’re enrolled.")
        return

    spend_by_class = approved_spend_by_class_for_cfo(mine, enrolled_names)
    valid_enrolled = [c for c in enrolled_names if c in all_teacher_names]

    if menu == STUDENT_NAV_ALL_ORDERS:
        st.subheader("All orders")
        st.caption(
            "Every line you’ve submitted across classes, oldest first. "
            "Open **My Classes** for budgets and **New order**."
        )
        render_student_orders_all_classes(mine, student_id=sid)
        return

    if menu == STUDENT_NAV_NOTIFICATIONS:
        st.subheader("Notifications")
        _render_notifications_panel(mine)
        return

    if menu == STUDENT_NAV_ENROLL:
        st.subheader("Enroll in a class")
        _render_extra_enroll_panel(sid, profile, teacher_class_rows)
        return

    # STUDENT_NAV_MY_CLASSES
    st.subheader("My classes")
    inject_class_expander_heading_styles()
    for i, cname in enumerate(valid_enrolled):
        total = float(budgets_map.get(cname, 0.0))
        spent = spend_by_class.get(cname, 0.0)
        remaining = total - spent
        util = (spent / total) if total > 0 else 0.0
        card_key = f"{stable_key(cname, 'sc')}_acc_{i}"
        cls_mine = mine[mine["class_name"] == cname].copy() if not mine.empty else pd.DataFrame()
        en_row = enroll_by_class.get(cname)

        with st.expander(cname, expanded=(i == 0)):
            qterm = quarter_map.get(cname, "")
            if qterm:
                st.caption(f"Quarter: **{qterm}**")
            if en_row:
                st.caption(
                    f"Name on requests: **{en_row['cfo_name']}** · Team **#{en_row['team_number']}** · "
                    f"_{en_row['team_name']}_"
                )
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric("Class budget", f"${total:,.2f}")
            with mc2:
                st.metric("Your approved spend", f"${spent:,.2f}")
            with mc3:
                st.metric("Remaining", f"${remaining:,.2f}")
            if total > 0:
                pct = min(100.0, util * 100.0)
                try:
                    st.progress(min(1.0, util), text=f"{pct:.0f}% of class budget used")
                except TypeError:
                    st.progress(min(1.0, util))
                    st.caption(f"{pct:.0f}% of class budget used")
            else:
                st.caption("No budget has been set for this class yet.")
            if spent > total and total > 0:
                st.warning("Your approved spend exceeds this class budget.")

            st.markdown("###### Your orders")
            render_student_orders_for_class(cls_mine, student_id=sid, key_prefix=card_key)
            st.divider()
            st.button(
                "New Order",
                type="primary",
                use_container_width=True,
                key=f"{card_key}_submit",
                on_click=open_student_order_form,
                args=(cname,),
            )
