import streamlit as st


def teacher_start_delete_class(cn: str) -> None:
    st.session_state.teacher_delete_confirm_class = cn


def teacher_cancel_delete_class() -> None:
    st.session_state.teacher_delete_confirm_class = None
