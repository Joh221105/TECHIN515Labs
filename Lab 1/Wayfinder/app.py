"""
Wayfinder — GIX campus resource finder (Streamlit app).
"""

from __future__ import annotations

import hashlib
import html
import textwrap

import pandas as pd
import streamlit as st

from search_heading import render_search_results_heading

st.set_page_config(
    page_title="Wayfinder",
    page_icon="🧭",
    layout="wide",
)

_UW_PURPLE = "#4B2E83"
_UW_PURPLE_SOFT = "rgba(75, 46, 131, 0.12)"
_UW_TEXT = "#2A1F3D"


def _inject_wayfinder_styles() -> None:
    st.markdown(
        textwrap.dedent(
            f"""
            <style>
              .block-container {{
                padding-top: 1.25rem;
                padding-bottom: 3rem;
                max-width: 960px;
              }}
              .wf-hero {{
                background: linear-gradient(135deg, {_UW_PURPLE} 0%, #6b4ba3 55%, #8b6bbd 100%);
                color: #fff;
                border-radius: 16px;
                padding: 1.75rem 1.5rem 1.5rem;
                margin-bottom: 1.25rem;
                box-shadow: 0 8px 28px rgba(75, 46, 131, 0.25);
              }}
              .wf-hero h1 {{
                margin: 0 0 0.35rem 0;
                font-size: 2rem;
                font-weight: 700;
                letter-spacing: -0.02em;
                line-height: 1.15;
                display: flex;
                align-items: center;
                gap: 0.45rem;
              }}
              .wf-hero p {{
                margin: 0;
                opacity: 0.92;
                font-size: 1.05rem;
                line-height: 1.45;
              }}
              .wf-metrics [data-testid="stMetricValue"] {{
                font-size: 1.65rem;
              }}
              div[data-testid="stVerticalBlockBorderWrapper"] {{
                border-radius: 14px !important;
                border: 1px solid rgba(75, 46, 131, 0.14) !important;
                background: linear-gradient(180deg, #ffffff 0%, #faf8fc 100%);
                box-shadow: 0 4px 18px rgba(42, 31, 61, 0.06);
                padding: 0.35rem 0.5rem 0.65rem;
              }}
              .wf-cat {{
                display: inline-block;
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                color: {_UW_PURPLE};
                background: {_UW_PURPLE_SOFT};
                padding: 0.25rem 0.7rem;
                border-radius: 999px;
                margin-bottom: 0.4rem;
              }}
              .wf-loc {{
                color: #5c4d6e;
                font-size: 0.95rem;
                line-height: 1.45;
                margin: 0.15rem 0 0.6rem 0;
              }}
              .wf-desc {{
                color: {_UW_TEXT};
                font-size: 1rem;
                line-height: 1.55;
                margin: 0 0 0.75rem 0;
              }}
              .wf-tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.35rem;
                margin: 0 0 0.5rem 0;
              }}
              .wf-tag {{
                font-size: 0.78rem;
                font-weight: 500;
                color: #4a3f5c;
                background: #ede8f4;
                border: 1px solid rgba(75, 46, 131, 0.12);
                padding: 0.15rem 0.55rem;
                border-radius: 999px;
              }}
              .wf-map-cap {{
                font-size: 0.85rem;
                color: #5c4d6e;
                margin: 0.25rem 0 0.35rem 0;
              }}
              .wf-footer {{
                margin-top: 2rem;
                padding-top: 1rem;
                border-top: 1px solid rgba(75, 46, 131, 0.12);
                color: #6e627d;
                font-size: 0.85rem;
              }}
              [data-testid="stMetric"] {{
                background: linear-gradient(180deg, #faf8fc 0%, #f3eef9 100%);
                border: 1px solid rgba(75, 46, 131, 0.12);
                border-radius: 12px;
                padding: 0.55rem 0.75rem;
              }}
            </style>
            """
        ),
        unsafe_allow_html=True,
    )

RESOURCE_KEYS: frozenset[str] = frozenset(
    {
        "name",
        "category",
        "location",
        # Illustrative coordinates (fictional placement around the GIX building footprint).
        "lat",
        "lon",
        "hours",
        "access",
        "description",
        "tags",
        "cost",
        "contact",
    }
)

RESOURCES: list[dict[str, object]] = [
    {
        "name": "GIX Makerspace",
        "category": "Makerspace",
        "location": "Steve Ballmer Building — Prototyping Lab (check door signage)",
        "hours": "Mon–Fri 9:00–21:00; weekends by reservation for capstone teams",
        "access": "GIX student/staff Husky Card tap; orientation required before solo use",
        "description": "Laser cutters, 3D printers, hand tools, and electronics benches for physical prototyping. Staff can help with machine training and material questions.",
        "tags": ["3d-printing", "laser", "electronics", "prototyping", "training"],
        "cost": "Included for enrolled students; specialty materials billed at cost",
        "contact": "makerspace@gix.uw.edu",
        "lat": 47.6197,
        "lon": -122.18545,
    },
    {
        "name": "Indoor bike storage",
        "category": "Transportation",
        "location": "Ground floor, secure card-access bike room near main entrance",
        "hours": "Building access hours (typically 7:00–22:00)",
        "access": "Husky Card; register your bike sticker at front desk once per quarter",
        "description": "Covered racks and repair stand with basic tools. Best for commuters using the Spring District / Link connections.",
        "tags": ["bike", "commuter", "storage", "sustainability"],
        "cost": "Free",
        "contact": None,
        "lat": 47.61958,
        "lon": -122.18515,
    },
    {
        "name": "Student free printing",
        "category": "Academic support",
        "location": "Copy alcove next to the student kitchen",
        "hours": "Mon–Fri 8:00–18:00 (toner restocked weekdays)",
        "access": "GIX netID login at the release station",
        "description": "Grayscale printing for course readings and posters up to tabloid size. Large format jobs go through the makerspace queue instead.",
        "tags": ["printing", "coursework", "netid"],
        "cost": "Free within fair-use quota; overages routed to department billing",
        "contact": "ithelp@gix.uw.edu",
        "lat": 47.61968,
        "lon": -122.18528,
    },
    {
        "name": "Quiet study room",
        "category": "Study space",
        "location": "Third floor, north wing — rooms 3xx (bookable pods)",
        "hours": "24/7 for students with building access",
        "access": "Reserve 2-hour blocks in the room tablet; no food, drinks with lids only",
        "description": "Small enclosed pods optimized for deep work, interviews, and timed assessments. White noise generators available at the desk.",
        "tags": ["quiet", "focus", "reservation", "interviews"],
        "cost": "Free",
        "contact": None,
        "lat": 47.61978,
        "lon": -122.1855,
    },
    {
        "name": "Collaborative studio",
        "category": "Study space",
        "location": "Second floor open studio overlooking the atrium",
        "hours": "Building access hours; after-hours for project teams on roster",
        "access": "Open seating; large tables first-come for teams of 3+",
        "description": "Writable walls, modular furniture, and portable monitors for design jams and sprint reviews. Nearby huddle rooms can be booked for calls.",
        "tags": ["teamwork", "whiteboards", "design", "sprint"],
        "cost": "Free",
        "contact": "frontdesk@gix.uw.edu",
        "lat": 47.61965,
        "lon": -122.18532,
    },
    {
        "name": "Graduate student lounge",
        "category": "Community",
        "location": "Fourth floor lounge with kitchenette and lockers",
        "hours": "24/7 graduate access",
        "access": "MSTI / related graduate programs; Husky Card tier 2",
        "description": "Microwave, fridge space, coffee fund jar, and bulletin board for rideshares. Respect quiet hours after 22:00.",
        "tags": ["lounge", "kitchen", "community", "msti"],
        "cost": "Free; coffee contributions optional",
        "contact": None,
        "lat": 47.61982,
        "lon": -122.18538,
    },
    {
        "name": "IT help desk",
        "category": "Technology",
        "location": "First floor service desk (shared with front-of-house)",
        "hours": "Mon–Fri 9:00–17:00; emergency pager after hours for classroom A/V",
        "access": "Walk-up or ticket; bring laptop and charger",
        "description": "Wi‑Fi troubleshooting, MFA resets, loaner adapters, and classroom hybrid kit checkouts.",
        "tags": ["wifi", "laptop", "av", "support", "tickets"],
        "cost": "Free for supported devices; replacement parts at UW rates",
        "contact": "ithelp@gix.uw.edu",
        "lat": 47.6196,
        "lon": -122.18522,
    },
    {
        "name": "Career services (GIX)",
        "category": "Career",
        "location": "Hybrid — coach office hours on-site Tuesdays; Zoom the rest of the week",
        "hours": "Coaching Tue 12:00–17:00 on campus; workshops announced on Slack #careers",
        "access": "Book via Handshake; MSTI students prioritized during recruiting season",
        "description": "Resume reviews, mock interviews, employer info sessions, and startup treks coordinated with Seattle and Bellevue partners.",
        "tags": ["jobs", "interviews", "handshake", "recruiting"],
        "cost": "Free for enrolled students",
        "contact": "gixcareers@uw.edu",
        "lat": 47.61963,
        "lon": -122.18518,
    },
]

for _resource in RESOURCES:
    assert set(_resource.keys()) == RESOURCE_KEYS, (
        f"Resource {_resource.get('name', '?')!r} must have exactly keys {sorted(RESOURCE_KEYS)}"
    )
    _tags = _resource["tags"]
    assert isinstance(_tags, list) and all(isinstance(t, str) for t in _tags)
    _contact = _resource["contact"]
    assert _contact is None or isinstance(_contact, str)
    assert isinstance(_resource["lat"], (int, float))
    assert isinstance(_resource["lon"], (int, float))

_CATEGORY_OPTIONS: list[str] = ["All"] + sorted(
    {str(r["category"]) for r in RESOURCES}
)


def search_resources(query: str, category: str) -> list[dict]:
    """Filter ``RESOURCES`` by category and optional keyword substring."""

    def category_ok(resource: dict[str, object]) -> bool:
        if category == "All":
            return True
        return str(resource["category"]).strip() == category.strip()

    # Strip first so whitespace-only queries behave like an empty search; then
    # lowercase so mixed-case queries match a lowercased haystack.
    needle = query.strip().lower()
    if not needle:

        def keyword_ok(_resource: dict[str, object]) -> bool:
            return True

    else:

        def keyword_ok(resource: dict[str, object]) -> bool:
            tags_obj = resource["tags"]
            assert isinstance(tags_obj, list)
            tag_strs = " ".join(str(t) for t in tags_obj)
            haystack = " ".join(
                [
                    str(resource["name"]),
                    str(resource["description"]),
                    str(resource["category"]),
                    tag_strs,
                ]
            ).lower()
            return needle in haystack

    return [r for r in RESOURCES if category_ok(r) and keyword_ok(r)]


def _resource_map_widget_key(resource: dict[str, object]) -> str:
    """Stable key for per-resource map widgets (checkbox + optional future controls)."""
    digest = hashlib.sha256(str(resource["name"]).encode("utf-8")).hexdigest()[:16]
    return f"wf_map_chk_{digest}"


def _render_resource_map(resource: dict[str, object]) -> None:
    """Single-point map using ``st.map`` only (no pydeck). ``size`` is radius in meters — keep small for a dot, not a blob."""
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
            options=_CATEGORY_OPTIONS,
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
            contact = resource["contact"]
            contact_line = str(contact) if contact is not None else "Not listed"
            tags_display = ", ".join(str(t) for t in tags_obj)
            tags_html = "".join(
                f'<span class="wf-tag">{html.escape(str(t))}</span>' for t in tags_obj
            )

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

                chk_key = _resource_map_widget_key(resource)
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
