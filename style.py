"""The only custom CSS on the site. Colors come from .streamlit/config.toml.

Everything here is a small, optional tweak. If a future Streamlit update ignores
one of these rules, the site still works, it just looks a little plainer.
"""

import streamlit as st


def _theme(option: str, fallback: str) -> str:
    try:
        return st.get_option(f"theme.{option}") or fallback
    except Exception:
        return fallback


def apply() -> None:
    orange = _theme("primaryColor", "#FF5F05")
    navy = _theme("textColor", "#13294B")
    st.html(
        f"""
        <style>
        /* Navy text on orange buttons: white on Illinois orange is too low-contrast to read easily. */
        [data-testid="stBaseButton-primary"], [data-testid="stBaseLinkButton-primary"],
        [data-testid="stBaseButton-primary"] p, [data-testid="stBaseLinkButton-primary"] p {{
            color: {navy} !important;
            font-weight: 600;
        }}
        /* Dog photos: same height on every card so the grid lines up. */
        .isd-card-photo img, [data-testid="stImage"] img {{
            aspect-ratio: 4 / 3;
            object-fit: cover;
            border-radius: 0.5rem;
        }}
        .isd-header {{
            border-bottom: 4px solid {orange};
            padding-bottom: 0.4rem;
            margin-bottom: 0.25rem;
        }}
        .isd-header .isd-name {{ font-size: 1.35rem; font-weight: 700; color: {navy}; }}
        .isd-header .isd-tagline {{ font-size: 0.95rem; color: {navy}; }}
        .isd-footer {{ font-size: 0.9rem; line-height: 1.6; }}
        /* Visible keyboard focus for links and buttons. */
        a:focus-visible, button:focus-visible {{
            outline: 3px solid {navy} !important;
            outline-offset: 2px;
        }}
        </style>
        """
    )
