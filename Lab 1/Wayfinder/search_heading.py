"""
Full-width search results heading bar (Streamlit).

This app uses a vertical sidebar (Streamlit default), not a horizontal navbar.
The bar is ``position: fixed`` under the Streamlit app header and spans
``calc(100vw - var(--sidebar-width, …))`` so it does not cover the sidebar.

Note on “every keystroke”: standard ``st.text_input`` typically reruns the script
when the field loses focus or the user presses Enter, not on each key. Live
per-key updates would require a custom component or extra dependency.
"""

from __future__ import annotations

import html
import logging
import textwrap
from typing import Any

import streamlit as st

_LOG = logging.getLogger(__name__)

# Matches Wayfinder subheader / metric headline scale (see app injected CSS).
_HEADING_FONT_REM = "1.65rem"
_HEADING_WEIGHT = "700"

_LOADING_PLACEHOLDER = "—"
_CSS_STATE_KEY = "_wf_search_results_bar_css_injected"


def format_count_for_heading(results: list[dict[str, Any]] | None, *, loading: bool) -> str:
    """
    Return the count segment for the heading (digits, ``0``, or em dash).

    - ``loading=True`` → em dash placeholder.
    - ``results is None`` → log warning, return ``\"0\"`` (graceful degradation).
    """
    if loading:
        return _LOADING_PLACEHOLDER
    if results is None:
        _LOG.warning("[SearchHeading] results data was null or undefined")
        return "0"
    return str(len(results))


def inject_search_results_bar_styles() -> None:
    """Inject fixed-bar CSS once per browser session (Streamlit rerun-safe)."""
    if st.session_state.get(_CSS_STATE_KEY):
        return
    st.session_state[_CSS_STATE_KEY] = True
    st.markdown(
        textwrap.dedent(
            f"""
            <style>
              /* Fixed strip under Streamlit header; width = viewport minus vertical sidebar */
              .wf-search-results-bar-fixed {{
                position: fixed;
                top: 3.5rem;
                left: var(--sidebar-width, 21rem);
                width: calc(100vw - var(--sidebar-width, 21rem));
                z-index: 1000002;
                box-sizing: border-box;
                margin: 0;
                padding: 0.7rem 1.25rem;
                min-height: 3.25rem;
                display: flex;
                align-items: center;
                background: #ffffff;
                border-bottom: 1px solid rgba(50, 0, 110, 0.14);
                box-shadow: 0 2px 8px rgba(42, 31, 61, 0.06);
              }}
              .wf-search-results-bar-inner {{
                font-size: {_HEADING_FONT_REM};
                font-weight: {_HEADING_WEIGHT};
                line-height: 1.2;
                letter-spacing: -0.02em;
                margin: 0;
                width: 100%;
              }}
              .wf-search-results-bar-inner .wf-srb-label {{
                color: #32006e;
              }}
              .wf-search-results-bar-inner .wf-srb-colon,
              .wf-search-results-bar-inner .wf-srb-count {{
                color: #000000;
              }}
              /* Reserves vertical space so fixed bar does not overlap the hero / list */
              .wf-search-results-bar-spacer {{
                height: 3.85rem;
                margin: 0 0 0.75rem 0;
                flex-shrink: 0;
              }}
              @media (max-width: 768px) {{
                .wf-search-results-bar-fixed {{
                  left: 0;
                  width: 100vw;
                }}
              }}
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def render_search_results_heading(
    results: list[dict[str, Any]] | None,
    *,
    loading: bool = False,
) -> None:
    """
    Render the fixed “Search Results: [n]” bar plus an in-flow spacer.

    ``results`` should be the same list used to render cards; pass ``None`` only
    if data failed to load (see ``format_count_for_heading``).
    """
    inject_search_results_bar_styles()
    count_str = html.escape(format_count_for_heading(results, loading=loading))
    st.markdown(
        f'<div class="wf-search-results-bar-fixed" role="status" aria-live="polite">'
        f'<p class="wf-search-results-bar-inner">'
        f'<span class="wf-srb-label">Search Results</span>'
        f'<span class="wf-srb-colon">: </span>'
        f'<span class="wf-srb-count">{count_str}</span>'
        f"</p>"
        f"</div>"
        f'<div class="wf-search-results-bar-spacer" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
