"""
Wayfinder — GIX campus resource finder (Streamlit UI only).
"""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from data import CATEGORY_OPTIONS, RESOURCES, search_resources
from search_heading import render_search_results_heading
from utils import (
    contact_display_line,
    resource_map_widget_key,
    resource_tags_html,
    wayfinder_theme_css,
)

st.set_page_config(
    page_title="Wayfinder",
    page_icon="🧭",
    layout="wide",
)


def _inject_wayfinder_styles() -> None:
    st.markdown(wayfinder_theme_css(), unsafe_allow_html=True)


def _render_resource_map(resource: dict[str, object]) -> None:
    """Single-point map: ``st.map`` with a small radius in meters."""
    lat = float(resource["lat"])
    lon = float(resource["lon"])
    df = pd.DataFrame({"lat": [lat], "lon": [lon]})
    st.markdown(
        '<p class="wf-map-cap">📍 Approximate location (illustrative map — not for navigation)</p>',
        unsafe_allow_html=True,
    )
    st.map(
        df,
        zoom=18,
        use_container_width=True,
        height=260,
        size=2,
        color="#4B2E83",
    )


def main() -> None:
    _inject_wayfinder_styles()

    with st.sidebar:
        st.markdown("### Filters")
        st.caption("Search and category apply to the list. Maps load only when you opt in per card.")
        st.divider()
        keyword = st.text_input(
            "Keyword",
            placeholder="e.g. printing, wifi, lounge…",
            help="Matches name, description, category, and tags. "
            "Streamlit reruns when you leave this field or press Enter (not on every keystroke).",
        )
        category = st.selectbox(
            "Category",
            options=CATEGORY_OPTIONS,
            help='Choose "All" to search every category.',
        )

    results = search_resources(keyword, category)

    render_search_results_heading(results, loading=False)

    st.markdown(
        """
        <div class="wf-hero">
          <h1><span aria-hidden="true">🧭</span> Wayfinder</h1>
          <p>GIX campus resource finder — browse services, spaces, and support in one place.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.metric("Resources in catalog", len(RESOURCES))

    st.divider()

    if not results:
        st.info(
            "No resources match these filters. Try clearing the keyword, setting category to **All**, "
            "or shorter terms like **print**, **study**, **bike**, or a tag such as **wifi**."
        )
    else:
        for resource in results:
            tags_obj = resource["tags"]
            assert isinstance(tags_obj, list)
            contact_line = contact_display_line(resource["contact"])
            tags_display = ", ".join(str(t) for t in tags_obj)
            tags_html = resource_tags_html([str(t) for t in tags_obj])

            with st.container(border=True):
                st.markdown(
                    f'<span class="wf-cat">{html.escape(str(resource["category"]))}</span>',
                    unsafe_allow_html=True,
                )
                st.subheader(str(resource["name"]))
                st.markdown(
                    f'<p class="wf-loc">📍 {html.escape(str(resource["location"]))}</p>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<p class="wf-desc">{html.escape(str(resource["description"]))}</p>',
                    unsafe_allow_html=True,
                )
                st.markdown(f'<div class="wf-tags">{tags_html}</div>', unsafe_allow_html=True)

                chk_key = resource_map_widget_key(resource)
                if st.checkbox("Show location on map", key=chk_key):
                    _render_resource_map(resource)

                with st.expander("Hours, access & contact"):
                    d1, d2 = st.columns(2, gap="large")
                    with d1:
                        st.markdown("**Hours**")
                        st.write(str(resource["hours"]))
                        st.markdown("**Access**")
                        st.write(str(resource["access"]))
                    with d2:
                        st.markdown("**Contact**")
                        st.write(contact_line)
                        st.markdown("**Tags**")
                        st.caption(tags_display)

    st.markdown(
        '<p class="wf-footer">Data maintained by GIX Student Services.</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
