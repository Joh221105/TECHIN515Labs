import streamlit as st

from procuregix.ui.uw_theme import (
    NAV_PRIMARY_BORDER,
    NAV_PRIMARY_GRADIENT,
    NAV_PRIMARY_GRADIENT_HOVER,
    NAV_PRIMARY_SHADOW,
    UW_GOLD,
    UW_GOLD_DARK,
    UW_PURPLE,
    UW_PURPLE_DEEP,
    UW_SECONDARY_BG,
)


def inject_teacher_navbar_styles() -> None:
    """Scoped chrome for the instructor header strip (uses Streamlit st-key-* when available)."""
    st.markdown(
        "<style>"
        "div.st-key-pgx_teacher_nav {"
        f"background: linear-gradient(180deg, {UW_PURPLE_DEEP} 0%, {UW_PURPLE} 100%);"
        "border-radius: 12px;"
        f"border: 1px solid rgba(183, 165, 122, 0.45);"
        "box-shadow: 0 4px 18px rgba(53, 32, 102, 0.25);"
        "padding: 0.35rem 0.5rem 0.5rem 0.5rem;"
        "}"
        "div.st-key-pgx_teacher_nav label, div.st-key-pgx_teacher_nav p, "
        "div.st-key-pgx_teacher_nav span { color: #f5f0fa !important; }"
        "div.st-key-pgx_teacher_nav [data-testid='stMarkdownContainer'] p { margin: 0; }"
        "div.st-key-pgx_teacher_nav button[kind='secondary'] {"
        "background: rgba(255,255,255,0.1) !important;"
        "color: #f8fafc !important;"
        f"border: 1px solid rgba(183, 165, 122, 0.5) !important;"
        "}"
        "div.st-key-pgx_teacher_nav button[kind='secondary']:hover {"
        "background: rgba(255,255,255,0.18) !important;"
        f"border-color: {UW_GOLD} !important;"
        "}"
        "div.st-key-pgx_teacher_nav button[kind='primary'] {"
        f"background: {UW_GOLD} !important;"
        f"border-color: {UW_GOLD_DARK} !important;"
        f"color: {UW_PURPLE_DEEP} !important;"
        "font-weight: 700 !important;"
        "}"
        "div.st-key-pgx_teacher_nav button[kind='primary']:hover {"
        f"background: #c9b896 !important;"
        f"border-color: {UW_PURPLE_DEEP} !important;"
        "}"
        "div.st-key-pgx_teacher_pw_panel {"
        f"background: {UW_SECONDARY_BG};"
        "border-radius: 12px;"
        f"border: 1px solid rgba(183, 165, 122, 0.45);"
        "padding: 0.75rem 1rem 1rem 1rem;"
        "margin-top: 0.25rem;"
        "margin-bottom: 0.5rem;"
        "box-shadow: 0 2px 10px rgba(75, 46, 131, 0.08);"
        "}"
        "</style>",
        unsafe_allow_html=True,
    )


def inject_admin_sidebar_nav_styles() -> None:
    """Vertical nav in the admin sidebar (student / instructor pattern)."""
    nav_btn = (
        "section[data-testid='stSidebar'] div.st-key-pgx_admin_nav_tabs button,"
        "section[data-testid='stSidebar'] div[class*='st-key-admin_nav_btn_'] button"
    )
    sec_fg = "#475569"
    hov_bg = "rgba(255,255,255,0.85)"
    hov_fg = "#0f172a"
    st.markdown(
        "<style>"
        "section[data-testid='stSidebar'] div.st-key-pgx_admin_nav_tabs {"
        "border: none !important;"
        "background: transparent !important;"
        "box-shadow: none !important;"
        "padding: 0;"
        "margin-bottom: 0.25rem;"
        "}"
        "section[data-testid='stSidebar'] div.st-key-pgx_admin_nav_tabs [data-testid='stVerticalBlock'] > div {"
        "gap: 1rem !important;"
        "}"
        f"{nav_btn} {{"
        "border-radius: 10px !important;"
        "font-weight: 600 !important;"
        "justify-content: flex-start !important;"
        "text-align: left !important;"
        "padding: 0.55rem 0.75rem !important;"
        "transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;"
        "}"
        f"{nav_btn}[kind='secondary'] {{"
        "background: transparent !important;"
        f"color: {sec_fg} !important;"
        "border: 1px solid transparent !important;"
        "box-shadow: none !important;"
        "}"
        f"{nav_btn}[kind='secondary']:hover {{"
        f"background: {hov_bg} !important;"
        "border-color: rgba(148, 163, 184, 0.45) !important;"
        f"color: {hov_fg} !important;"
        "}"
        f"{nav_btn}[kind='primary'] {{"
        f"background: {NAV_PRIMARY_GRADIENT} !important;"
        "color: #fff !important;"
        f"border: 2px solid {NAV_PRIMARY_BORDER} !important;"
        f"box-shadow: {NAV_PRIMARY_SHADOW};"
        "}"
        f"{nav_btn}[kind='primary']:hover {{"
        f"background: {NAV_PRIMARY_GRADIENT_HOVER} !important;"
        f"border-color: {UW_GOLD} !important;"
        "}"
        "</style>",
        unsafe_allow_html=True,
    )


def inject_teacher_sidebar_nav_styles() -> None:
    """Vertical nav in the teacher sidebar: tab-like buttons, selected state emphasized."""
    nav_btn = (
        "section[data-testid='stSidebar'] div.st-key-pgx_teacher_nav_tabs button,"
        "section[data-testid='stSidebar'] div[class*='st-key-teacher_nav_btn_'] button"
    )
    sec_fg = "#475569"
    hov_bg = "rgba(255,255,255,0.85)"
    hov_fg = "#0f172a"
    st.markdown(
        "<style>"
        "section[data-testid='stSidebar'] div.st-key-pgx_teacher_nav_tabs {"
        "border: none !important;"
        "background: transparent !important;"
        "box-shadow: none !important;"
        "padding: 0;"
        "margin-bottom: 0.25rem;"
        "}"
        "section[data-testid='stSidebar'] div.st-key-pgx_teacher_nav_tabs [data-testid='stVerticalBlock'] > div {"
        "gap: 1rem !important;"
        "}"
        f"{nav_btn} {{"
        "border-radius: 10px !important;"
        "font-weight: 600 !important;"
        "justify-content: flex-start !important;"
        "text-align: left !important;"
        "padding: 0.55rem 0.75rem !important;"
        "transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;"
        "}"
        f"{nav_btn}[kind='secondary'] {{"
        "background: transparent !important;"
        f"color: {sec_fg} !important;"
        "border: 1px solid transparent !important;"
        "box-shadow: none !important;"
        "}"
        f"{nav_btn}[kind='secondary']:hover {{"
        f"background: {hov_bg} !important;"
        "border-color: rgba(148, 163, 184, 0.45) !important;"
        f"color: {hov_fg} !important;"
        "}"
        f"{nav_btn}[kind='primary'] {{"
        f"background: {NAV_PRIMARY_GRADIENT} !important;"
        "color: #fff !important;"
        f"border: 2px solid {NAV_PRIMARY_BORDER} !important;"
        f"box-shadow: {NAV_PRIMARY_SHADOW};"
        "}"
        f"{nav_btn}[kind='primary']:hover {{"
        f"background: {NAV_PRIMARY_GRADIENT_HOVER} !important;"
        f"border-color: {UW_GOLD} !important;"
        "}"
        "</style>",
        unsafe_allow_html=True,
    )


def inject_student_sidebar_nav_styles() -> None:
    """Vertical nav in the student sidebar (same pattern as instructor)."""
    nav_btn = (
        "section[data-testid='stSidebar'] div.st-key-pgx_student_nav_tabs button,"
        "section[data-testid='stSidebar'] div[class*='st-key-student_nav_btn_'] button"
    )
    sec_fg = "#475569"
    hov_bg = "rgba(255,255,255,0.85)"
    hov_fg = "#0f172a"
    st.markdown(
        "<style>"
        "section[data-testid='stSidebar'] div.st-key-pgx_student_nav_tabs {"
        "border: none !important;"
        "background: transparent !important;"
        "box-shadow: none !important;"
        "padding: 0;"
        "margin-bottom: 0.25rem;"
        "}"
        "section[data-testid='stSidebar'] div.st-key-pgx_student_nav_tabs [data-testid='stVerticalBlock'] > div {"
        "gap: 1rem !important;"
        "}"
        f"{nav_btn} {{"
        "border-radius: 10px !important;"
        "font-weight: 600 !important;"
        "justify-content: flex-start !important;"
        "text-align: left !important;"
        "padding: 0.55rem 0.75rem !important;"
        "transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;"
        "}"
        f"{nav_btn}[kind='secondary'] {{"
        "background: transparent !important;"
        f"color: {sec_fg} !important;"
        "border: 1px solid transparent !important;"
        "box-shadow: none !important;"
        "}"
        f"{nav_btn}[kind='secondary']:hover {{"
        f"background: {hov_bg} !important;"
        "border-color: rgba(148, 163, 184, 0.45) !important;"
        f"color: {hov_fg} !important;"
        "}"
        f"{nav_btn}[kind='primary'] {{"
        f"background: {NAV_PRIMARY_GRADIENT} !important;"
        "color: #fff !important;"
        f"border: 2px solid {NAV_PRIMARY_BORDER} !important;"
        f"box-shadow: {NAV_PRIMARY_SHADOW};"
        "}"
        f"{nav_btn}[kind='primary']:hover {{"
        f"background: {NAV_PRIMARY_GRADIENT_HOVER} !important;"
        f"border-color: {UW_GOLD} !important;"
        "}"
        "</style>",
        unsafe_allow_html=True,
    )


def inject_student_order_filter_nav_styles() -> None:
    """Horizontal filter tabs on student order lists: same blocky look as student sidebar nav."""
    wrap = "section.main div[class*='st-key-pgx_student_order_filter_']"
    nav_btn = f"{wrap} button"
    sec_fg = "#475569"
    hov_bg = "rgba(241, 245, 249, 0.95)"
    hov_fg = "#0f172a"
    st.markdown(
        "<style>"
        f"{wrap} {{"
        "border: none !important;"
        "background: transparent !important;"
        "box-shadow: none !important;"
        "padding: 0;"
        "margin-bottom: 0.35rem;"
        "}"
        f"{wrap} [data-testid='stHorizontalBlock'] {{"
        "gap: 0.45rem !important;"
        "}"
        f"{nav_btn} {{"
        "border-radius: 10px !important;"
        "font-weight: 600 !important;"
        "justify-content: center !important;"
        "text-align: center !important;"
        "padding: 0.5rem 0.35rem !important;"
        "transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;"
        "}"
        f"{nav_btn}[kind='secondary'] {{"
        "background: transparent !important;"
        f"color: {sec_fg} !important;"
        "border: 1px solid rgba(148, 163, 184, 0.55) !important;"
        "box-shadow: none !important;"
        "}"
        f"{nav_btn}[kind='secondary']:hover {{"
        f"background: {hov_bg} !important;"
        "border-color: rgba(148, 163, 184, 0.75) !important;"
        f"color: {hov_fg} !important;"
        "}"
        f"{nav_btn}[kind='primary'] {{"
        f"background: {NAV_PRIMARY_GRADIENT} !important;"
        "color: #fff !important;"
        f"border: 2px solid {NAV_PRIMARY_BORDER} !important;"
        f"box-shadow: {NAV_PRIMARY_SHADOW};"
        "}"
        f"{nav_btn}[kind='primary']:hover {{"
        f"background: {NAV_PRIMARY_GRADIENT_HOVER} !important;"
        f"border-color: {UW_GOLD} !important;"
        "}"
        "</style>",
        unsafe_allow_html=True,
    )


def inject_teacher_order_action_styles() -> None:
    """Green Approve and red Reject on the teacher Orders → Pending tab (works inside tabs)."""
    # Streamlit 1.45+ element classes look like st-key-$$ID-<md5>-<user_key>; match user_key suffix.
    def _btn(sel: str) -> str:
        return f"{sel} button, {sel} [data-testid='stButton'] button"

    def _btn_h(sel: str) -> str:
        return f"{sel} button:hover, {sel} [data-testid='stButton'] button:hover"

    appr_w = "[class*='pgx_ord_appr_']"
    rej_w = "[class*='pgx_ord_rej_']"
    conf_w = "[class*='pgx_ord_confirm_rej_']"
    appr_k = "[class*='ta_appr_']"
    rej_k = "[class*='ta_reject_']"
    conf_k = "[class*='ta_confirm_rej_']"
    st.markdown(
        "<style>"
        f"{_btn(appr_w)}, {_btn(appr_k)} {{"
        "background: #16a34a !important;"
        "background-color: #16a34a !important;"
        "background-image: none !important;"
        "border-color: #15803d !important;"
        "color: #fff !important;"
        "}}"
        f"{_btn_h(appr_w)}, {_btn_h(appr_k)} {{"
        "background: #22c55e !important;"
        "background-color: #22c55e !important;"
        "border-color: #16a34a !important;"
        "color: #fff !important;"
        "}}"
        f"{_btn(rej_w)}, {_btn(rej_k)} {{"
        "background: #dc2626 !important;"
        "background-color: #dc2626 !important;"
        "background-image: none !important;"
        "border-color: #b91c1c !important;"
        "color: #fff !important;"
        "}}"
        f"{_btn_h(rej_w)}, {_btn_h(rej_k)} {{"
        "background: #ef4444 !important;"
        "background-color: #ef4444 !important;"
        "border-color: #dc2626 !important;"
        "color: #fff !important;"
        "}}"
        f"{_btn(conf_w)}, {_btn(conf_k)} {{"
        "background: #b91c1c !important;"
        "background-color: #b91c1c !important;"
        "background-image: none !important;"
        "border-color: #991b1b !important;"
        "color: #fff !important;"
        "}}"
        f"{_btn_h(conf_w)}, {_btn_h(conf_k)} {{"
        "background: #dc2626 !important;"
        "background-color: #dc2626 !important;"
        "border-color: #b91c1c !important;"
        "color: #fff !important;"
        "}}"
        "</style>",
        unsafe_allow_html=True,
    )


def inject_teacher_order_detail_card_styles() -> None:
    """Larger body text for teacher Orders → Pending / Approved horizontal cards."""
    def _rule(suffix: str) -> str:
        return (
            f"[class*='pgx_pending_card_'] [data-testid='stMarkdownContainer']{suffix}, "
            f"[class*='pgx_approved_card_'] [data-testid='stMarkdownContainer']{suffix}"
        )

    body_color = ""
    link_color = f"{UW_PURPLE} !important;"
    st.markdown(
        "<style>"
        f"{_rule(' p')} {{"
        "font-size: 1.2rem !important;"
        "line-height: 1.55 !important;"
        f"{body_color}"
        "}}"
        f"{_rule(' a')} {{"
        "font-size: 1.2rem !important;"
        f"color: {link_color}"
        "}}"
        f"{_rule(' strong')} {{"
        "font-size: inherit !important;"
        "}}"
        "</style>",
        unsafe_allow_html=True,
    )


def inject_teacher_pending_order_card_styles() -> None:
    """Backward-compatible name; use inject_teacher_order_detail_card_styles."""
    inject_teacher_order_detail_card_styles()


def inject_class_expander_heading_styles() -> None:
    sum_color = f"color: {UW_PURPLE} !important;"
    st.markdown(
        "<style>"
        "section.main [data-testid='stExpander'] details > summary {"
        "font-size: 1.85rem !important;"
        "font-weight: 700 !important;"
        "line-height: 1.3;"
        "letter-spacing: 0.01em;"
        f"{sum_color}"
        "}"
        "section.main [data-testid='stExpander'] details > summary p,"
        "section.main [data-testid='stExpander'] details > summary span {"
        "font-size: 1.85rem !important;"
        "font-weight: 700 !important;"
        f"{sum_color}"
        "}"
        "</style>",
        unsafe_allow_html=True,
    )


def inject_admin_quarter_workspace_typography() -> None:
    """Larger body text inside each admin term workspace (captions, class accordions, tables)."""
    sel = "section.main div[class*='st-key-pgx_admin_qw_']"
    st.markdown(
        "<style>"
        f"{sel} [data-testid='stMarkdownContainer'] p, "
        f"{sel} [data-testid='stMarkdownContainer'] li, "
        f"{sel} [data-testid='stCaption'], "
        f"{sel} [data-testid='stAlert'] p {{"
        "font-size: 1.2rem !important;"
        "line-height: 1.55 !important;"
        "}}"
        f"{sel} [data-testid='stMarkdownContainer'] h3 {{"
        "font-size: 1.45rem !important;"
        "margin-top: 0.75rem !important;"
        "margin-bottom: 0.35rem !important;"
        "}}"
        f"{sel} [data-testid='stMarkdownContainer'] h4, "
        f"{sel} [data-testid='stMarkdownContainer'] h5, "
        f"{sel} [data-testid='stMarkdownContainer'] h6 {{"
        "font-size: 1.25rem !important;"
        "}}"
        f"{sel} button[kind='primary'], {sel} button[kind='secondary'] {{"
        "font-size: 1.1rem !important;"
        "min-height: 2.75rem !important;"
        "}}"
        f"{sel} [data-testid='stWidgetLabel'] p, "
        f"{sel} [data-baseweb='form-control'] label {{"
        "font-size: 1.05rem !important;"
        "}}"
        f"{sel} .glide-data-grid, "
        f"{sel} .dvn-scroller {{"
        "font-size: 1.05rem !important;"
        "}}"
        "</style>",
        unsafe_allow_html=True,
    )
