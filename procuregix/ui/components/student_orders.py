from __future__ import annotations

import hashlib
import html

import pandas as pd
import streamlit as st

from db import delete_pending_order_line_for_student

from procuregix.config import STUDENT_STATUS_BG
from procuregix.ui.student.actions import start_resubmit
from procuregix.ui.styles import inject_student_order_filter_nav_styles
from procuregix.utils.formatting import parse_created_display, student_status_label


def student_orders_sorted_by_submission(m: pd.DataFrame) -> pd.DataFrame:
    """Chronological order: earliest submitted first; tie-break by row id when present."""
    if m.empty:
        return m
    m = m.copy()
    if "created_at" not in m.columns:
        return m.reset_index(drop=True)
    by = ["created_at"]
    ascending = [True]
    if "id" in m.columns:
        by.append("id")
        ascending.append(True)
    return m.sort_values(by, ascending=ascending).reset_index(drop=True)


def _pending_mask(m: pd.DataFrame) -> pd.Series:
    return m["status"].astype(str).str.lower().str.strip() == "pending"


def _approved_mask(m: pd.DataFrame) -> pd.Series:
    return m["status"].astype(str).str.lower().str.strip() == "approved"


def _rejected_mask(m: pd.DataFrame) -> pd.Series:
    return m["status"].astype(str).str.lower().str.strip() == "rejected"


def _ordered_filter_mask(m: pd.DataFrame) -> pd.Series:
    """Fulfillment-style statuses for the Ordered filter (excludes pending, approved, rejected)."""
    s = m["status"].astype(str).str.lower().str.strip()
    return s.isin({"ordered", "received", "backordered", "returned_refunded", "archived"})


def _columns_row(spec: list[float]):
    """st.columns with a small gap when the runtime supports it (tighter row layout)."""
    try:
        return st.columns(spec, gap="small")
    except TypeError:
        return st.columns(spec)


def _order_grid_scoped_css(scope_frag: str) -> None:
    """Vertical dividers + center cell content under headings for the class order grid."""
    # Streamlit may suffix keys; match the user key fragment inside the generated class.
    hb = f"section.main div[class*='{scope_frag}'] div[data-testid='stHorizontalBlock']"
    col = f"{hb} > div"
    st.markdown(
        "<style>"
        f"{col} {{"
        "display: flex !important;"
        "flex-direction: column !important;"
        "align-items: center !important;"
        "text-align: center !important;"
        "}}"
        f"{col}:not(:first-child) {{"
        "border-left: 1px solid rgba(148, 163, 184, 0.55);"
        "padding-left: 0.5rem !important;"
        "margin-left: 0 !important;"
        "}}"
        f"{hb} [data-testid='stMarkdownContainer'],"
        f"{hb} [data-testid='stMarkdownContainer'] p {{"
        "text-align: center !important;"
        "}}"
        f"{hb} [data-testid='stCaption'],"
        f"{hb} [data-testid='stCaption'] p {{"
        "text-align: center !important;"
        "}}"
        f"{hb} [data-testid='stText'] {{"
        "text-align: center !important;"
        "}}"
        f"{hb} .stButton, {hb} [data-testid='stBaseButton-secondary'],"
        f"{hb} [data-testid='stBaseButton-primary'] {{"
        "display: flex !important;"
        "justify-content: center !important;"
        "width: 100% !important;"
        "}}"
        f"{hb} [data-testid='stLinkButton'], {hb} .stLinkButton {{"
        "display: flex !important;"
        "justify-content: center !important;"
        "width: 100% !important;"
        "}}"
        f"{hb} a {{"
        "display: inline-block;"
        "text-align: center;"
        "}}"
        "</style>",
        unsafe_allow_html=True,
    )


def _link_cell(link_url: str) -> None:
    u = (link_url or "").strip()
    if not u:
        st.caption("—")
        return
    low = u.lower()
    if low.startswith("javascript:"):
        st.caption("—")
        return
    if hasattr(st, "link_button"):
        st.link_button("Open link", u, use_container_width=True)
    else:
        href = html.escape(u, quote=True)
        st.markdown(
            f'<a href="{href}" target="_blank" rel="noopener noreferrer">Open link</a>',
            unsafe_allow_html=True,
        )


def _student_order_filter_wrap_key(key_prefix: str) -> str:
    """Stable unique fragment for st.container + CSS (avoids duplicate widget keys across classes)."""
    frag = hashlib.md5(key_prefix.encode("utf-8")).hexdigest()[:12]
    return f"pgx_student_order_filter_{frag}"


def _render_student_order_show_filter(key_prefix: str, options: tuple[str, ...]) -> str:
    """Blocky tab buttons (student sidebar style) instead of radio; returns selected label."""
    inject_student_order_filter_nav_styles()
    state_key = f"{key_prefix}_order_filter_choice"
    if state_key not in st.session_state or st.session_state[state_key] not in options:
        st.session_state[state_key] = options[0]
    choice = str(st.session_state[state_key])

    st.caption("Show")
    with st.container(key=_student_order_filter_wrap_key(key_prefix)):
        try:
            cols = st.columns(len(options), gap="small")
        except TypeError:
            cols = st.columns(len(options))
        for col, opt in zip(cols, options):
            with col:
                selected = choice == opt
                if st.button(
                    opt,
                    key=f"{key_prefix}_show_f_{opt}",
                    type="primary" if selected else "secondary",
                    use_container_width=True,
                ):
                    if st.session_state[state_key] != opt:
                        st.session_state[state_key] = opt
                        st.rerun()
    return str(st.session_state[state_key])


def _filter_orders_by_show_choice(m: pd.DataFrame, choice: str) -> pd.DataFrame:
    if m.empty:
        return m
    if choice == "All":
        return m
    if choice == "Pending":
        return m[_pending_mask(m)].copy()
    if choice == "Approved":
        return m[_approved_mask(m)].copy()
    if choice == "Ordered":
        return m[_ordered_filter_mask(m)].copy()
    if choice == "Rejected":
        return m[_rejected_mask(m)].copy()
    return m


def _render_unified_order_rows(
    mf: pd.DataFrame,
    *,
    student_id: int | None,
    key_prefix: str,
    show_class_column: bool,
) -> None:
    """Shared grid: optional Class column + Item, Link, Qty, Price, Provider, Status, Submitted, actions."""
    if mf.empty:
        return
    scope_seed = f"{key_prefix}:{'all' if show_class_column else 'cls'}"
    sk = "pgx_oc_" + hashlib.md5(scope_seed.encode("utf-8")).hexdigest()[:14]
    _order_grid_scoped_css(sk)

    if show_class_column:
        col_weights = [1.05, 1.45, 1.05, 0.5, 0.72, 0.95, 0.92, 1.12, 0.68]
        labels = ["Class", "Item", "Link", "Qty", "Price", "Provider", "Status", "Submitted", ""]
    else:
        col_weights = [1.55, 1.05, 0.5, 0.72, 0.95, 0.92, 1.2, 0.7]
        labels = ["Item", "Link", "Qty", "Price", "Provider", "Status", "Submitted", ""]

    with st.container(key=sk):
        hdr = _columns_row(col_weights)
        for col, lab in zip(hdr, labels):
            with col:
                st.caption(lab)

        rows = list(mf.iterrows())
        for idx, (_, row) in enumerate(rows):
            raw_st = str(row["status"])
            st_low = raw_st.strip().lower()
            pv = float(row["unit_price"])
            qv = float(row["quantity"])
            q_disp = int(qv) if float(qv).is_integer() else qv
            status_label = html.escape(student_status_label(raw_st))
            bg = STUDENT_STATUS_BG.get(st_low, "#f1f5f9")
            link_raw = str(row.get("link_url") or "")

            cols = _columns_row(col_weights)
            if show_class_column:
                (
                    cx_class,
                    cx_item,
                    cx_link,
                    cx_qty,
                    cx_price,
                    cx_prov,
                    cx_stat,
                    cx_sub,
                    cx_act,
                ) = cols
                with cx_class:
                    st.markdown(f"**{row['class_name']}**")
            else:
                (
                    cx_item,
                    cx_link,
                    cx_qty,
                    cx_price,
                    cx_prov,
                    cx_stat,
                    cx_sub,
                    cx_act,
                ) = cols
            with cx_item:
                st.markdown(f"**{row['item_name']}**")
            with cx_link:
                _link_cell(link_raw)
            with cx_qty:
                st.text(str(q_disp))
            with cx_price:
                st.text(f"${pv:,.2f}")
            with cx_prov:
                st.text(str(row["provider"]))
            with cx_stat:
                st.markdown(
                    f'<span style="display:inline-block;background-color:{bg};padding:0.2rem 0.5rem;'
                    f"border-radius:6px;font-size:0.88rem;font-weight:600;\">{status_label}</span>",
                    unsafe_allow_html=True,
                )
            with cx_sub:
                st.text(parse_created_display(str(row["created_at"])))
            with cx_act:
                if student_id is not None and st_low == "pending":
                    oid = int(row["id"])
                    if st.button(
                        "Remove",
                        key=f"{key_prefix}_rm_{oid}",
                        use_container_width=True,
                    ):
                        ok, err = delete_pending_order_line_for_student(oid, student_id)
                        if ok:
                            st.session_state["student_order_flash"] = "Removed."
                            st.rerun()
                        else:
                            st.error(err)
                elif student_id is not None and st_low == "rejected":
                    oid = int(row["id"])
                    st.button(
                        "Resubmit",
                        key=f"{key_prefix}_rs_{oid}",
                        use_container_width=True,
                        on_click=start_resubmit,
                        args=(oid,),
                    )
            if idx < len(rows) - 1:
                st.divider()


def render_student_orders_for_class(
    mine_class: pd.DataFrame,
    student_id: int | None = None,
    *,
    key_prefix: str = "s1cls",
) -> None:
    """Per-class orders: same Show filters as All orders (including Rejected)."""
    if mine_class.empty:
        st.caption("No orders for this class yet.")
        return

    choice = _render_student_order_show_filter(
        key_prefix, ("All", "Pending", "Approved", "Ordered", "Rejected")
    )

    m = student_orders_sorted_by_submission(mine_class)
    filtered = _filter_orders_by_show_choice(m, choice)

    if filtered.empty:
        st.caption(f"No **{choice.lower()}** orders in this class.")
        return

    _render_unified_order_rows(
        filtered,
        student_id=student_id,
        key_prefix=key_prefix,
        show_class_column=False,
    )


def render_student_orders_all_classes(
    mine_all: pd.DataFrame,
    student_id: int | None = None,
    *,
    key_prefix: str = "sall",
) -> None:
    """All order lines: same row grid as My Classes, with a Class column + Show filter."""
    if mine_all.empty:
        st.caption("You have no order lines yet. Submit requests from **My Classes**.")
        return

    choice = _render_student_order_show_filter(
        key_prefix, ("All", "Pending", "Approved", "Ordered", "Rejected")
    )

    m = student_orders_sorted_by_submission(mine_all)
    filtered = _filter_orders_by_show_choice(m, choice)

    if filtered.empty:
        st.caption(f"No **{choice.lower()}** orders yet.")
        return

    _render_unified_order_rows(
        filtered,
        student_id=student_id,
        key_prefix=key_prefix,
        show_class_column=True,
    )
