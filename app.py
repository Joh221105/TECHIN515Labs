"""
ProcureGIX — entrypoint for `streamlit run app.py`.
Application logic lives in the `procuregix` package.
"""

from __future__ import annotations

import streamlit as st

from procuregix.main import main

st.set_page_config(
    page_title="ProcureGIX",
    page_icon="📋",
    layout="wide",
)

if __name__ == "__main__":
    main()
