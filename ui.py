"""Shared building blocks for pages: header, footer, buttons, dog cards.

Rule of thumb used everywhere: a Sheet cell that is blank or still says
[ISD to confirm] is simply not shown to visitors. The Content Check page lists
every one of those cells so the board knows what to fill in.
"""

from __future__ import annotations

import html

import streamlit as st

import config
from content import (
    get_site_text,
    is_placeholder,
    mailto,
    photo_path,
    safe_url,
)

PAGES = {
    "home": "pages/home.py",
    "dogs": "pages/meet_the_dogs.py",
    "sponsor": "pages/sponsor_donate.py",
    "apply": "pages/apply.py",
    "involved": "pages/get_involved.py",
    "events": "pages/events.py",
    "about": "pages/about.py",
    "ask": "pages/ask_isd.py",
    "check": "pages/content_check.py",
}


def text(key: str, default: str = "") -> str:
    """SiteText value, or default if it is blank or still a placeholder."""
    value = get_site_text(key)
    return default if is_placeholder(value) else value


def show(value) -> str:
    """A cell from any tab, or "" if it is blank or still a placeholder."""
    return "" if is_placeholder(value) else str(value)


def md(value) -> str:
    """Make Sheet text safe for Streamlit markdown: a $ sign would otherwise start a math formula."""
    return str(value or "").replace("$", "\\$")


def say(value) -> None:
    """Show a paragraph of Sheet text."""
    st.markdown(md(value))


def esc(value) -> str:
    return html.escape(str(value or ""))


def email_link(key: str) -> str:
    """Markdown link for a SiteText email key, e.g. [donate@...](mailto:donate@...)."""
    email = text(key)
    return f"[{email}]({mailto(email)})" if mailto(email) else ""


def link_button(label: str, url: str, *, primary: bool = False, key: str | None = None) -> bool:
    """Button that opens an outside link. Shows nothing if the link isn't set yet."""
    url = safe_url(url) or (url if str(url).startswith("mailto:") else "")
    if not url:
        return False
    st.link_button(label, url, type="primary" if primary else "secondary", width="stretch", key=key)
    return True


def go_button(label: str, page: str, *, primary: bool = True, key: str | None = None) -> None:
    """Big button that moves to another page of this site."""
    if st.button(label, type="primary" if primary else "secondary", width="stretch", key=key):
        st.switch_page(PAGES[page])


def header() -> None:
    st.html(
        f'<div class="isd-header" role="banner">'
        f'<div class="isd-name">🐾 {esc(text("org_name", "Illini Service Dogs"))}</div>'
        f'<div class="isd-tagline">{esc(text("tagline"))}</div>'
        f"</div>"
    )


def footer() -> None:
    st.divider()
    parts = []
    if text("address"):
        parts.append(esc(text("address")))
    contact = text("contact_email")
    if mailto(contact):
        line = f'Email: <a href="{esc(mailto(contact))}">{esc(contact)}</a>'
        if text("response_time"):
            line += f" · {esc(text('response_time'))}"
        parts.append(line)
    socials = []
    for key, label in (("instagram_url", "Instagram"), ("facebook_url", "Facebook")):
        if safe_url(get_site_text(key)):
            socials.append(f'<a href="{esc(safe_url(get_site_text(key)))}" target="_blank" '
                           f'rel="noopener">Illini Service Dogs on {label}</a>')
    if socials:
        parts.append(" · ".join(socials))
    parts.append("Content updated from ISD's Google Sheet.")
    st.html(f'<footer class="isd-footer" role="contentinfo">{"<br>".join(parts)}</footer>')


def placeholder_svg(name: str) -> str:
    """Neutral stand-in image used until a real photo is uploaded."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300">'
        '<rect width="400" height="300" fill="#F4F1EC"/>'
        '<text x="200" y="140" font-size="64" text-anchor="middle">🐾</text>'
        f'<text x="200" y="205" font-size="28" text-anchor="middle" fill="#13294B" '
        f'font-family="sans-serif">{esc(name)}</text>'
        '<text x="200" y="240" font-size="16" text-anchor="middle" fill="#13294B" '
        'font-family="sans-serif">Photo coming soon</text></svg>'
    )


def dog_photo(dog: dict) -> None:
    path = photo_path(dog.get("photo_file"))
    if path:
        alt = show(dog.get("alt_text")) or f"Photo of {dog['name']}, an Illini Service Dog"
        st.image(str(path), alt=alt, width="stretch")
    else:
        st.image(placeholder_svg(dog["name"]), alt=f"Placeholder: photo of {dog['name']} coming soon",
                 width="stretch")


def training_progress(stage) -> None:
    if stage in config.TRAINING_STAGES:
        label = f"Stage {stage} of {len(config.TRAINING_STAGES)}: {config.TRAINING_STAGES[stage]}"
        st.progress(stage / len(config.TRAINING_STAGES), text=label)


def dog_card(dog: dict, *, with_sponsor: bool = True, key_prefix: str = "dog") -> None:
    with st.container(border=True):
        dog_photo(dog)
        st.subheader(md(dog["name"]))
        facts = [f for f in (show(dog.get("breed")), show(dog.get("age"))) if f]
        if facts:
            st.caption(md(" · ".join(facts)))
        if show(dog.get("bio")):
            say(show(dog["bio"]))
        training_progress(dog.get("training_stage"))
        insta = safe_url(dog.get("instagram_url"))
        if insta:
            st.markdown(f"[Follow {md(dog['name'])} on Instagram]({insta})")
        if with_sponsor:
            label = f"Sponsor {dog['name']}"
            if not link_button(label, dog.get("sponsor_link", ""), primary=True,
                               key=f"{key_prefix}-sponsor-{dog.get('_pos', 0)}"):
                go_button(label, "sponsor", key=f"{key_prefix}-sponsor-{dog.get('_pos', 0)}")


def grid(items: list[dict], render, columns: int = 3) -> None:
    """Lay items out in rows of `columns`. Streamlit stacks them on phones automatically."""
    for start in range(0, len(items), columns):
        cols = st.columns(columns)
        for col, item in zip(cols, items[start:start + columns]):
            with col:
                render({**item, "_pos": start + cols.index(col)})


def nice_date(d) -> str:
    """Saturday, March 14, 2027 (works on every operating system)."""
    return f"{d:%A, %B} {d.day}, {d.year}"


def event_card(event: dict, *, heading_level: str = "subheader") -> None:
    with st.container(border=True):
        getattr(st, heading_level)(md(event["title"]))
        when = nice_date(event["date"])
        if show(event.get("start_time")):
            when += f" at {event['start_time']}"
        say(f"**When:** {when}")
        if show(event.get("location")):
            say(f"**Where:** {event['location']}")
        if show(event.get("description")):
            say(event["description"])
        link_button(f"Details for {event['title']}", event.get("link", ""), key=f"event-{event.get('_pos', 0)}")
