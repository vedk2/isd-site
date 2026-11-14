"""All custom styling for the site, in one place.

Colors come from .streamlit/config.toml. Most rules style the site's own HTML
blocks (classes starting with "isd-"), which Streamlit upgrades don't touch.
The few rules that reach into Streamlit's own parts are marked; if an upgrade
ignores one, the site still works and just looks a little plainer.
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
    cream = _theme("secondaryBackgroundColor", "#F7F3EE")
    st.html(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800;900&display=swap');
        :root {{
            --isd-orange: {orange};
            --isd-navy: {navy};
            --isd-cream: {cream};
            --isd-orange-soft: #FFF1E8;
            --isd-orange-dark: #C84113;   /* Illinois "Altgeld" orange, readable on white */
            --isd-radius: 18px;
            --isd-shadow: 0 6px 24px rgba(19, 41, 75, 0.10);
        }}

        /* ---- Streamlit's own parts (small, optional tweaks) ---- */
        h1, h2, h3, .isd-display {{ font-family: 'Nunito', 'Source Sans Pro', sans-serif !important; letter-spacing: -0.01em; }}
        h1, h2, h3 {{ color: var(--isd-navy); }}
        [data-testid="stBaseButton-primary"], [data-testid="stBaseLinkButton-primary"],
        [data-testid="stBaseButton-primary"] p, [data-testid="stBaseLinkButton-primary"] p {{
            color: var(--isd-navy) !important; font-weight: 700;   /* navy on orange passes contrast; white doesn't */
        }}
        [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"],
        [data-testid="stBaseLinkButton-primary"], [data-testid="stBaseLinkButton-secondary"] {{ border-radius: 999px; }}
        [data-testid="stExpander"] details {{ border-radius: 14px; }}
        .block-container {{ padding-top: 3.2rem; max-width: 1180px; }}
        a:focus-visible, button:focus-visible, summary:focus-visible {{
            outline: 3px solid var(--isd-navy) !important; outline-offset: 2px;
        }}

        /* ---- Header and footer ---- */
        .isd-header {{ display: flex; align-items: center; gap: 14px; padding: 6px 0 14px;
            border-bottom: 1px solid rgba(19,41,75,0.12); margin-bottom: 8px; }}
        .isd-header img {{ width: 56px; height: 56px; border-radius: 50%; }}
        .isd-header .isd-name {{ font-family: 'Nunito', sans-serif; font-weight: 900; font-size: 1.35rem; color: var(--isd-navy); line-height: 1.1; }}
        .isd-header .isd-tagline {{ font-size: 0.92rem; color: var(--isd-navy); opacity: 0.85; }}
        .isd-header .isd-spacer {{ flex: 1; }}
        .isd-footer {{ background: var(--isd-navy); color: #fff; border-radius: var(--isd-radius);
            padding: 28px 28px 22px; margin-top: 8px; display: grid; gap: 18px;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); font-size: 0.95rem; line-height: 1.6; }}
        .isd-footer a {{ color: #fff; }}
        .isd-footer .isd-foot-title {{ font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 1.05rem; margin-bottom: 4px; }}
        .isd-footer .isd-small {{ grid-column: 1 / -1; opacity: 0.8; font-size: 0.85rem; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 10px; }}

        /* ---- Buttons made of links ---- */
        .isd-btn {{ display: inline-block; padding: 0.7rem 1.35rem; border-radius: 999px; font-weight: 800;
            text-decoration: none !important; font-family: 'Nunito', sans-serif; margin: 4px 8px 4px 0;
            border: 2px solid var(--isd-orange); transition: transform .12s ease; }}
        .isd-btn:hover {{ transform: translateY(-1px); }}
        .isd-btn-primary {{ background: var(--isd-orange); color: var(--isd-navy) !important; }}
        .isd-btn-ghost {{ background: transparent; color: var(--isd-navy) !important; border-color: var(--isd-navy); }}
        .isd-btn-light {{ background: #fff; color: var(--isd-navy) !important; border-color: #fff; }}

        /* ---- Hero ---- */
        .isd-hero {{ display: grid; grid-template-columns: 1.1fr 1fr; gap: 36px; align-items: center;
            background: linear-gradient(135deg, var(--isd-cream) 0%, var(--isd-orange-soft) 100%);
            border-radius: 28px; padding: 40px; margin: 6px 0 26px; }}
        .isd-hero .isd-eyebrow {{ text-transform: uppercase; letter-spacing: .12em; font-weight: 800; font-size: .8rem; color: var(--isd-orange-dark); }}
        .isd-hero h1 {{ font-size: clamp(2.1rem, 4.2vw, 3.4rem); line-height: 1.05; margin: 8px 0 14px; padding: 0; }}
        .isd-hero p {{ font-size: 1.12rem; line-height: 1.6; color: var(--isd-navy); }}
        .isd-hero img {{ width: 100%; aspect-ratio: 4 / 3.4; object-fit: cover; border-radius: 22px; box-shadow: var(--isd-shadow); }}
        .isd-pagehead {{ background: linear-gradient(135deg, var(--isd-cream) 0%, var(--isd-orange-soft) 100%);
            border-radius: 24px; padding: 30px 34px; margin: 6px 0 24px; }}
        .isd-pagehead h1 {{ font-size: clamp(1.9rem, 3.6vw, 2.8rem); margin: 0 0 6px; padding: 0; }}
        .isd-pagehead p {{ font-size: 1.08rem; max-width: 760px; margin: 0; color: var(--isd-navy); }}

        /* ---- Sections and grids ---- */
        .isd-section-title {{ font-family: 'Nunito', sans-serif; font-weight: 900; font-size: 1.75rem; color: var(--isd-navy); margin: 26px 0 4px; }}
        .isd-lead {{ font-size: 1.05rem; color: var(--isd-navy); margin-bottom: 14px; }}
        .isd-grid {{ display: grid; gap: 20px; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); margin: 10px 0 18px; }}
        .isd-grid-wide {{ grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }}
        .isd-card {{ background: #fff; border-radius: var(--isd-radius); box-shadow: var(--isd-shadow);
            overflow: hidden; display: flex; flex-direction: column; border: 1px solid rgba(19,41,75,0.06); }}
        .isd-card img.isd-photo {{ width: 100%; aspect-ratio: 4 / 4.4; object-fit: cover; display: block; }}
        .isd-card .isd-body {{ padding: 16px 18px 18px; display: flex; flex-direction: column; gap: 6px; flex: 1; }}
        .isd-card h3 {{ margin: 0; padding: 0; font-size: 1.35rem; }}
        .isd-card .isd-meta {{ font-size: .9rem; color: var(--isd-orange-dark); font-weight: 700; }}
        .isd-card p {{ margin: 0; line-height: 1.55; }}
        .isd-card .isd-actions {{ margin-top: auto; padding-top: 8px; }}
        .isd-tag {{ display: inline-block; background: var(--isd-orange-soft); color: var(--isd-orange-dark);
            border-radius: 999px; padding: 2px 10px; font-size: .78rem; font-weight: 800; }}
        .isd-progress {{ background: #EEE7DF; border-radius: 999px; height: 10px; overflow: hidden; }}
        .isd-progress span {{ display: block; height: 100%; background: var(--isd-orange); border-radius: 999px; }}
        .isd-placeholder {{ aspect-ratio: 4 / 4.4; background: var(--isd-cream); display: flex; align-items: center;
            justify-content: center; flex-direction: column; color: var(--isd-navy); font-weight: 700; }}

        /* ---- Stats strip ---- */
        .isd-stats {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); margin: 4px 0 18px; }}
        .isd-stat {{ background: var(--isd-navy); color: #fff; border-radius: var(--isd-radius); padding: 20px 22px; }}
        .isd-stat b {{ display: block; font-family: 'Nunito', sans-serif; font-size: 2rem; font-weight: 900; color: var(--isd-orange); }}

        /* ---- Split block (photo + text) ---- */
        .isd-split {{ display: grid; grid-template-columns: 1fr 1fr; gap: 32px; align-items: center; margin: 18px 0 26px; }}
        .isd-split img {{ width: 100%; border-radius: 22px; aspect-ratio: 4 / 3; object-fit: cover; box-shadow: var(--isd-shadow); }}
        .isd-split p {{ font-size: 1.05rem; line-height: 1.7; }}
        .isd-callout {{ background: var(--isd-navy); color: #fff; border-radius: 24px; padding: 30px 34px; margin: 22px 0; }}
        .isd-callout h2 {{ color: #fff; margin: 0 0 8px; padding: 0; }}
        .isd-callout p {{ color: #fff; font-size: 1.05rem; }}

        /* ---- Steps ---- */
        .isd-steps {{ counter-reset: step; display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); margin: 8px 0 18px; padding: 0; list-style: none; }}
        .isd-steps li {{ background: #fff; border-radius: var(--isd-radius); box-shadow: var(--isd-shadow); padding: 18px; position: relative; }}
        .isd-steps li::before {{ counter-increment: step; content: counter(step); display: inline-flex; width: 34px; height: 34px;
            border-radius: 50%; background: var(--isd-orange); color: var(--isd-navy); font-weight: 900; align-items: center; justify-content: center; margin-bottom: 8px; }}
        .isd-steps b {{ display: block; font-family: 'Nunito', sans-serif; font-size: 1.1rem; }}

        /* ---- Giving levels ---- */
        .isd-levels {{ display: grid; gap: 14px; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); margin: 8px 0 18px; }}
        .isd-level {{ border: 2px solid #EFE6DC; border-radius: var(--isd-radius); padding: 16px 18px; background: #fff; }}
        .isd-level b {{ font-family: 'Nunito', sans-serif; font-size: 1.6rem; font-weight: 900; color: var(--isd-navy); display: block; }}
        .isd-level.isd-featured {{ border-color: var(--isd-orange); background: var(--isd-orange-soft); }}

        /* ---- People ---- */
        .isd-people {{ display: grid; gap: 18px; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); margin: 8px 0 22px; }}
        .isd-person {{ text-align: center; }}
        .isd-person img, .isd-person .isd-initials {{ width: 120px; height: 120px; border-radius: 50%; object-fit: cover;
            object-position: center 25%; box-shadow: var(--isd-shadow); border: 4px solid #fff; }}
        .isd-person .isd-initials {{ display: inline-flex; align-items: center; justify-content: center; background: var(--isd-cream);
            font-family: 'Nunito', sans-serif; font-weight: 900; font-size: 2rem; color: var(--isd-navy); }}
        .isd-person b {{ display: block; margin-top: 8px; }}
        .isd-person span {{ font-size: .88rem; color: var(--isd-navy); opacity: .85; }}

        /* ---- Logos and gallery ---- */
        .isd-logos {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); align-items: stretch; margin: 8px 0 18px; }}
        .isd-logo {{ background: #fff; border-radius: 14px; border: 1px solid #EFE6DC; padding: 14px; display: flex; align-items: center;
            justify-content: center; min-height: 96px; text-align: center; font-weight: 800; color: var(--isd-navy); text-decoration: none; }}
        .isd-logo img {{ max-width: 100%; max-height: 70px; object-fit: contain; }}
        .isd-gallery {{ columns: 4 220px; column-gap: 14px; margin: 8px 0 18px; }}
        .isd-gallery figure {{ break-inside: avoid; margin: 0 0 14px; }}
        .isd-gallery img {{ width: 100%; border-radius: 14px; display: block; }}
        .isd-gallery figcaption {{ font-size: .8rem; margin-top: 4px; color: var(--isd-navy); opacity: .8; }}

        /* ---- News ---- */
        .isd-news {{ display: grid; gap: 22px; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); margin: 8px 0 18px; }}
        .isd-news img.isd-photo {{ aspect-ratio: 16 / 10; }}
        .isd-news details summary {{ cursor: pointer; font-weight: 800; color: var(--isd-orange-dark); margin-top: 6px; }}
        .isd-news details p {{ margin: 8px 0 0; white-space: pre-line; }}

        @media (max-width: 760px) {{
            .isd-hero, .isd-split {{ grid-template-columns: 1fr; padding: 22px; gap: 18px; }}
            .isd-split {{ padding: 0; }}
            .isd-pagehead {{ padding: 22px; }}
            .isd-header img {{ width: 46px; height: 46px; }}
        }}
        </style>
        """
    )
