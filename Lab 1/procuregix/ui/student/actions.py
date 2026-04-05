from __future__ import annotations

import streamlit as st

from db import fetch_all_orders


def start_resubmit(order_id: int) -> None:
    for r in fetch_all_orders():
        if int(r["id"]) == int(order_id):
            st.session_state["student_resubmit_order"] = dict(r)
            st.session_state.student_view = "form"
            return


def open_student_order_form(class_name: str) -> None:
    st.session_state["student_form_preset_class"] = class_name
    st.session_state.student_view = "form"
