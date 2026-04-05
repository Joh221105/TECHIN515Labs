from __future__ import annotations

import uuid

import streamlit as st

from procuregix.config import PROVIDERS


def pgx_item_key(rid: str, field: str) -> str:
    return f"pgx_{rid}_{field}"


def ensure_item_row_ids() -> None:
    if "item_row_ids" not in st.session_state:
        st.session_state.item_row_ids = [uuid.uuid4().hex[:12]]


def reset_item_rows() -> None:
    for rid in list(st.session_state.item_row_ids):
        prefix = pgx_item_key(rid, "")
        for k in list(st.session_state.keys()):
            if k.startswith(prefix):
                del st.session_state[k]
    st.session_state.item_row_ids = [uuid.uuid4().hex[:12]]


def add_item_row() -> None:
    st.session_state.item_row_ids.append(uuid.uuid4().hex[:12])


def remove_item_row(rid: str) -> None:
    if len(st.session_state.item_row_ids) <= 1:
        return
    st.session_state.item_row_ids.remove(rid)
    prefix = pgx_item_key(rid, "")
    for k in list(st.session_state.keys()):
        if k.startswith(prefix):
            del st.session_state[k]


def apply_resubmit_to_form(payload: dict, class_options: list[str]) -> None:
    reset_item_rows()
    rid = st.session_state.item_row_ids[0]
    st.session_state[pgx_item_key(rid, "item_name")] = str(payload.get("item_name") or "")
    st.session_state[pgx_item_key(rid, "qty")] = float(payload.get("quantity") or 1)
    st.session_state[pgx_item_key(rid, "price")] = float(payload.get("unit_price") or 0)
    st.session_state[pgx_item_key(rid, "link")] = str(payload.get("link_url") or "")
    st.session_state[pgx_item_key(rid, "notes")] = str(payload.get("notes") or "")
    pr = str(payload.get("provider") or "")
    st.session_state[pgx_item_key(rid, "provider")] = pr if pr in PROVIDERS else PROVIDERS[0]
    cn = str(payload.get("class_name") or "")
    if cn in class_options:
        st.session_state["student_form_class"] = cn
    elif class_options:
        st.session_state["student_form_class"] = class_options[0]
        st.session_state["student_form_warning"] = (
            "Original class is no longer available; class was reset to the first option. Check before submitting."
        )
