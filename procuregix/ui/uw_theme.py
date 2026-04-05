"""
University of Washington–inspired purple and gold palette for ProcureGIX.

Based on common UW brand colors (purple and metallic gold). Use these constants
in CSS and keep `.streamlit/config.toml` [theme] aligned for Streamlit widgets.
"""

# Core brand
UW_PURPLE = "#4B2E83"
UW_PURPLE_DEEP = "#352066"
UW_PURPLE_BRIGHT = "#6B4C9A"
UW_GOLD = "#B7A57A"
UW_GOLD_DARK = "#8B7355"
UW_GOLD_PALE = "#F3EDE4"

# Light UI chrome (with Streamlit [theme])
UW_TEXT = "#2A1F3D"
UW_PAGE_BG = "#FFFFFF"
UW_SECONDARY_BG = "#F5F0FA"  # faint lavender

# Nav “primary” button (gradient + shadow)
NAV_PRIMARY_GRADIENT = (
    f"linear-gradient(135deg, {UW_PURPLE_DEEP} 0%, {UW_PURPLE} 100%)"
)
NAV_PRIMARY_GRADIENT_HOVER = (
    f"linear-gradient(135deg, {UW_PURPLE} 0%, {UW_PURPLE_BRIGHT} 100%)"
)
NAV_PRIMARY_BORDER = UW_GOLD
NAV_PRIMARY_SHADOW = "0 2px 10px rgba(75, 46, 131, 0.4)"
