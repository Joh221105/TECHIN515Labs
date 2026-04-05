from __future__ import annotations

import pandas as pd
import streamlit as st

from db import (
    enrollment_row_for_student_class,
    fetch_all_orders,
    fetch_all_teacher_classes,
    fetch_enrolled_class_names_for_student,
)

from procuregix.auth.session import _require_student_login, _session_student_account_id
from procuregix.config import PROVIDERS
from procuregix.utils.budget import approved_spend_by_class_for_cfo

from procuregix.ui.student.line_items import (
    add_item_row,
    apply_resubmit_to_form,
    ensure_item_row_ids,
    pgx_item_key,
    remove_item_row,
)
from procuregix.ui.student.order_confirm import (
    student_order_confirm_content,
    student_order_confirm_dialog,
)


def run_student_form() -> None:
    st.subheader("Submit an order request")

    form_warn = st.session_state.pop("student_form_warning", None)
    if form_warn:
        st.warning(form_warn)

    resubmit_payload = st.session_state.pop("student_resubmit_order", None)

    _require_student_login()
    sid = _session_student_account_id()
    assert sid is not None

    class_options = fetch_enrolled_class_names_for_student(sid)
    preset = st.session_state.pop("student_form_preset_class", None)

    if not class_options:
        st.warning(
            "You must **enroll in at least one class** on your dashboard before you can submit orders. "
            "There is no global submit button until you’re enrolled."
        )
        if st.button("Back to dashboard", type="primary"):
            st.session_state.student_view = "dashboard"
            st.rerun()
        return

    pending = st.session_state.get("student_order_confirm")
    if pending is not None:
        if pending.get("student_id") != sid:
            del st.session_state["student_order_confirm"]
        else:
            if hasattr(st, "dialog"):
                student_order_confirm_dialog()
            else:
                try:
                    review_box = st.container(border=True)
                except TypeError:
                    review_box = st.container()
                with review_box:
                    st.markdown("##### Review your order")
                    student_order_confirm_content(pending)
                st.stop()

    ensure_item_row_ids()

    if preset and preset in class_options:
        st.session_state["student_form_class"] = preset
    elif preset:
        st.session_state["student_form_warning"] = (
            "That class isn’t in your enrollments; choose a class below before submitting."
        )

    if resubmit_payload:
        apply_resubmit_to_form(resubmit_payload, class_options)

    cur_cls = st.session_state.get("student_form_class")
    if cur_cls not in class_options:
        st.session_state["student_form_class"] = class_options[0]
    class_name = str(st.session_state["student_form_class"])
    st.caption(f"Class: **{class_name}**")
    if enrollment_row_for_student_class(sid, class_name) is None:
        st.error("You’re not enrolled in the selected class. Return to the dashboard and enroll first.")
        if st.button("Back to dashboard", type="primary", key="student_form_bad_enroll_back"):
            st.session_state.student_view = "dashboard"
            st.rerun()
        return

    st.markdown("##### Items in this request")
    for idx, rid in enumerate(st.session_state.item_row_ids, start=1):
        c_a, c_b, c_c, c_rm = st.columns([3, 1, 1, 1])
        with c_a:
            st.text_input("Item name", max_chars=500, key=pgx_item_key(rid, "item_name"))
        with c_b:
            st.number_input(
                "Quantity",
                min_value=0.0,
                step=1.0,
                value=1.0,
                key=pgx_item_key(rid, "qty"),
            )
        with c_c:
            st.number_input(
                "Price (per unit, USD)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key=pgx_item_key(rid, "price"),
            )
        with c_rm:
            st.write("")
            st.write("")
            st.button(
                "Remove",
                key=f"pgx_rm_{rid}",
                disabled=len(st.session_state.item_row_ids) <= 1,
                on_click=remove_item_row,
                args=(rid,),
            )
        qv = float(st.session_state.get(pgx_item_key(rid, "qty"), 1.0) or 0.0)
        pv = float(st.session_state.get(pgx_item_key(rid, "price"), 0.0) or 0.0)
        line_total = qv * pv
        st.caption(f"Line total: **${line_total:,.2f}** ({qv:g} × ${pv:,.2f})")
        st.selectbox(
            "Provider / supplier",
            PROVIDERS,
            key=pgx_item_key(rid, "provider"),
        )
        st.text_input("Link to purchase", max_chars=2000, key=pgx_item_key(rid, "link"))
        st.text_area("Notes", max_chars=2000, height=100, key=pgx_item_key(rid, "notes"))
        st.divider()

    st.button("Add Another Item", on_click=add_item_row, type="secondary")

    bs, bc = st.columns(2)
    with bs:
        submitted = st.button("Submit order", type="primary", use_container_width=True)
    with bc:
        if st.button("Cancel", use_container_width=True, key="student_form_cancel"):
            st.session_state.student_view = "dashboard"
            st.rerun()

    if submitted:
        enrolled_now = fetch_enrolled_class_names_for_student(sid)
        if class_name not in enrolled_now:
            st.error(
                "You’re not enrolled in the selected class. Return to the dashboard and enroll, or pick another class."
            )
            return
        en_submit = enrollment_row_for_student_class(sid, class_name)
        if en_submit is None:
            st.error("Enrollment for this class is missing. Refresh and try again.")
            return
        cfo_name = str(en_submit["cfo_name"])
        team_number = int(en_submit["team_number"])
        lines: list[tuple[str, float, float, str, str, str]] = []
        errs: list[str] = []
        for idx, rid in enumerate(st.session_state.item_row_ids, start=1):
            item_name = (st.session_state.get(pgx_item_key(rid, "item_name")) or "").strip()
            link_url = (st.session_state.get(pgx_item_key(rid, "link")) or "").strip()
            notes = (st.session_state.get(pgx_item_key(rid, "notes")) or "").strip()
            qty = float(st.session_state.get(pgx_item_key(rid, "qty"), 0.0) or 0.0)
            price = float(st.session_state.get(pgx_item_key(rid, "price"), 0.0) or 0.0)
            prov_raw = st.session_state.get(pgx_item_key(rid, "provider"))
            provider_line = str(prov_raw) if prov_raw in PROVIDERS else PROVIDERS[0]

            row_errs = []
            if not item_name:
                row_errs.append("item name")
            if not link_url:
                row_errs.append("link to purchase")
            if qty <= 0:
                row_errs.append("quantity (must be > 0)")
            if row_errs:
                errs.append(f"Item {idx}: missing or invalid {', '.join(row_errs)}.")
            else:
                lines.append((item_name, qty, price, link_url, notes, provider_line))

        if errs:
            for e in errs:
                st.error(e)
            return

        request_total = sum(q * p for _, q, p, _, _, _ in lines)
        teacher_rows = fetch_all_teacher_classes()
        budgets_map = {r["class_name"]: float(r["budget_usd"]) for r in teacher_rows}
        class_budget = float(budgets_map.get(class_name, 0.0))
        spent_approved = 0.0
        if class_budget > 0:
            rows_all = fetch_all_orders()
            df_m = pd.DataFrame(rows_all) if rows_all else pd.DataFrame()
            mine_cfo = (
                df_m[
                    (df_m["cfo_name"] == cfo_name) & (df_m["class_name"] == class_name)
                ].copy()
                if not df_m.empty
                else pd.DataFrame()
            )
            spent_approved = approved_spend_by_class_for_cfo(mine_cfo, [class_name]).get(
                class_name, 0.0
            )
            if spent_approved + request_total > class_budget:
                remaining = max(0.0, class_budget - spent_approved)
                st.error(
                    "This order would exceed the class budget. "
                    f"Your approved spend for this class is **${spent_approved:,.2f}** of **${class_budget:,.2f}**; "
                    f"you have about **${remaining:,.2f}** left before hitting the cap, but this request totals **${request_total:,.2f}**. "
                    "Reduce quantities or remove items, then try again."
                )
                return

        st.session_state["student_order_confirm"] = {
            "student_id": sid,
            "cfo_name": cfo_name,
            "team_number": int(team_number),
            "class_name": class_name,
            "lines": lines,
            "request_total": request_total,
            "spent_approved": spent_approved,
            "class_budget": class_budget,
        }
        st.rerun()
