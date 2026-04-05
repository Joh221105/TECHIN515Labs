from __future__ import annotations

import uuid

import pandas as pd
import streamlit as st

from db import (
    enrollment_row_for_student_class,
    fetch_all_orders,
    fetch_all_teacher_classes,
    fetch_enrolled_class_names_for_student,
    insert_orders_group,
)

from procuregix.auth.session import _session_student_account_id
from procuregix.utils.budget import approved_spend_by_class_for_cfo

from procuregix.ui.student.line_items import reset_item_rows


def student_order_confirm_place(pending: dict) -> None:
    """Finalize order after review; re-check enrollment and budget."""
    raw_sid = pending.get("student_id")
    if raw_sid is None:
        del st.session_state["student_order_confirm"]
        st.session_state["student_form_warning"] = (
            "This review session expired. Please submit your order again from the dashboard."
        )
        st.rerun()
        return
    sid = int(raw_sid)
    cfo_name = str(pending["cfo_name"])
    team_number = int(pending["team_number"])
    class_name = str(pending["class_name"])
    lines: list[tuple[str, float, float, str, str, str]] = pending["lines"]
    request_total = float(pending["request_total"])

    enrolled_visible = fetch_enrolled_class_names_for_student(
        sid, visible_on_student_dashboard_only=True
    )
    if class_name not in enrolled_visible:
        del st.session_state["student_order_confirm"]
        st.session_state["student_form_warning"] = (
            "You’re not enrolled in that class anymore, or it was removed from your dashboard. "
            "Review your enrollments and try again."
        )
        st.rerun()
        return

    row = enrollment_row_for_student_class(sid, class_name)
    if row is None:
        del st.session_state["student_order_confirm"]
        st.session_state["student_form_warning"] = (
            "Enrollment for that class is missing. Return to the dashboard and enroll again."
        )
        st.rerun()
        return
    if str(row["cfo_name"]) != cfo_name or int(row["team_number"]) != team_number:
        del st.session_state["student_order_confirm"]
        st.session_state["student_form_warning"] = (
            "Your CFO or team details for this class changed since you started this order. "
            "Start a new request from the dashboard."
        )
        st.rerun()
        return

    teacher_rows = fetch_all_teacher_classes()
    budgets_map = {r["class_name"]: float(r["budget_usd"]) for r in teacher_rows}
    class_budget = float(budgets_map.get(class_name, 0.0))
    if class_budget > 0:
        rows_all = fetch_all_orders()
        df_m = pd.DataFrame(rows_all) if rows_all else pd.DataFrame()
        mine_cfo = (
            df_m[
                (df_m["cfo_name"] == cfo_name) & (df_m["class_name"] == class_name)
            ].copy()
            if not df_m.empty
            else df_m
        )
        spent_approved = approved_spend_by_class_for_cfo(mine_cfo, [class_name]).get(class_name, 0.0)
        if spent_approved + request_total > class_budget:
            del st.session_state["student_order_confirm"]
            st.session_state["student_form_warning"] = (
                "This order no longer fits the class budget (it may have changed). Adjust your request and try again."
            )
            st.rerun()
            return

    group_id = uuid.uuid4().hex
    ids = insert_orders_group(
        order_group_id=group_id,
        class_name=class_name,
        team_number=int(team_number),
        cfo_name=cfo_name,
        lines=lines,
    )
    del st.session_state["student_order_confirm"]
    reset_item_rows()
    st.session_state.student_view = "dashboard"
    n = len(ids)
    st.session_state["student_order_flash"] = (
        f"Submitted ({n} line{'s' if n != 1 else ''}). Your instructor will review the request."
    )
    st.rerun()


def student_order_confirm_content(pending: dict) -> None:
    """Compact review: lines (name, qty, line total), budget metrics, confirm / cancel."""
    lines: list[tuple[str, float, float, str, str, str]] = pending["lines"]
    request_total = float(pending["request_total"])
    spent_approved = float(pending["spent_approved"])
    class_budget = float(pending["class_budget"])

    h1, h2, h3 = st.columns([2.2, 0.7, 0.9])
    with h1:
        st.caption("Item")
    with h2:
        st.caption("Qty")
    with h3:
        st.caption("Total")

    for row in lines:
        item_name, qty, price, _link, _notes, _provider = row
        lt = float(qty) * float(price)
        q_disp = int(qty) if float(qty).is_integer() else qty
        c1, c2, c3 = st.columns([2.2, 0.7, 0.9])
        with c1:
            st.text(item_name)
        with c2:
            st.text(str(q_disp))
        with c3:
            st.text(f"${lt:,.2f}")

    st.divider()
    st.metric("Order total", f"{request_total:,.2f} USD")

    rem_after = max(0.0, class_budget - spent_approved - request_total)
    b1, b2 = st.columns(2)
    with b1:
        if class_budget > 0:
            st.metric("Current budget", f"{class_budget:,.2f} USD")
        else:
            st.metric("Current budget", "Not set")
    with b2:
        if class_budget > 0:
            st.metric("Leftover after purchase", f"{rem_after:,.2f} USD")
        else:
            st.metric("Leftover after purchase", "—")

    st.write("")
    c_ok, c_back = st.columns(2)
    with c_ok:
        if st.button("Confirm", type="primary", use_container_width=True, key="student_confirm_place"):
            student_order_confirm_place(pending)
    with c_back:
        if st.button("Cancel", use_container_width=True, key="student_confirm_back"):
            del st.session_state["student_order_confirm"]
            st.rerun()


@st.dialog("Review your order")
def student_order_confirm_dialog() -> None:
    pending = st.session_state.get("student_order_confirm")
    if not pending:
        return
    sid = _session_student_account_id()
    if sid is None or pending.get("student_id") != sid:
        del st.session_state["student_order_confirm"]
        return
    student_order_confirm_content(pending)
