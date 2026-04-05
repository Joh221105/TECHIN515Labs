from __future__ import annotations

import sqlite3

import streamlit as st

from db import insert_teacher_class

from procuregix.auth.session import _require_teacher_db_identity
from procuregix.config import SELECTABLE_QUARTERS


def run_teacher_add_class_form() -> None:
    teacher_name = _require_teacher_db_identity()
    flash = st.session_state.pop("teacher_class_flash", None)
    if flash:
        st.success(flash)
    st.subheader("Add new class")
    if st.button("← Back to my classes"):
        st.session_state.teacher_view = "list"
        st.rerun()

    st.selectbox(
        "Academic quarter for this class",
        options=SELECTABLE_QUARTERS,
        index=0,
        key="teacher_new_class_quarter",
        help="Only these program terms are available (no custom years). Class names must still be unique across the whole system.",
    )
    new_name = st.text_input("Class name", max_chars=200, key="teacher_new_class_name")
    new_budget = st.number_input(
        "Budget amount (USD)",
        min_value=0.0,
        step=50.0,
        format="%.2f",
        key="teacher_new_class_budget",
    )
    st.text_input(
        "Enrollment passcode (share with students)",
        type="password",
        max_chars=200,
        key="teacher_new_class_passcode",
        help="Students enter this when they enroll. Use something easy to share in class, not your personal password.",
    )

    if st.button("Create class", type="primary"):
        name = (new_name or "").strip()
        if not name:
            st.error("Class name is required.")
            return
        pc = (st.session_state.get("teacher_new_class_passcode") or "").strip()
        if not pc:
            st.error("Enrollment passcode is required so students can join your class.")
            return
        quarter = str(st.session_state.get("teacher_new_class_quarter") or SELECTABLE_QUARTERS[0])
        if quarter not in SELECTABLE_QUARTERS:
            st.error("Invalid term selection.")
            return
        try:
            insert_teacher_class(
                class_name=name,
                budget_usd=float(new_budget),
                teacher_name=teacher_name,
                enroll_passcode=pc,
                quarter=quarter,
            )
        except sqlite3.IntegrityError:
            st.error("A class with that name already exists. Choose a different name.")
            return
        st.session_state.teacher_view = "list"
        st.session_state["teacher_class_flash"] = (
            f"Created **{name}** for **{quarter}** with budget **${float(new_budget):,.2f}**."
        )
        st.rerun()
