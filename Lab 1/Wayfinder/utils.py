"""
Wayfinder — pure helpers (CSS string, widget keys, display fragments).
"""

from __future__ import annotations

import hashlib
import html
import textwrap

# Theme tokens (match ProcureGIX / `.streamlit/config.toml` where applicable)
UW_PURPLE = "#4B2E83"
UW_PURPLE_SOFT = "rgba(75, 46, 131, 0.12)"
UW_TEXT = "#2A1F3D"


def wayfinder_theme_css() -> str:
    """Return a ``<style>…</style>`` block for the Wayfinder layout (no Streamlit calls)."""
    return textwrap.dedent(
        f"""
        <style>
          .block-container {{
            padding-top: 1.25rem;
            padding-bottom: 3rem;
            max-width: 960px;
          }}
          .wf-hero {{
            background: linear-gradient(135deg, {UW_PURPLE} 0%, #6b4ba3 55%, #8b6bbd 100%);
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
            color: {UW_PURPLE};
            background: {UW_PURPLE_SOFT};
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
            color: {UW_TEXT};
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
    ).strip()


def resource_map_widget_key(resource: dict[str, object]) -> str:
    """Stable Streamlit widget key for per-resource map checkbox."""
    digest = hashlib.sha256(str(resource["name"]).encode("utf-8")).hexdigest()[:16]
    return f"wf_map_chk_{digest}"


def resource_tags_html(tags: list[str]) -> str:
    """Build escaped HTML chip markup for tag pills."""
    return "".join(f'<span class="wf-tag">{html.escape(str(t))}</span>' for t in tags)


def contact_display_line(contact: object) -> str:
    """Human-readable contact for UI; ``None`` becomes *Not listed*."""
    if contact is None:
        return "Not listed"
    return str(contact)
