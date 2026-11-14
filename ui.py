"""Shared building blocks for pages: header, footer, hero, cards and grids.

Two rules used everywhere:
- A Sheet cell that is blank or still says [ISD to confirm] is simply not shown
  to visitors. The Content Check page lists those cells so the board can fill them.
- Every <img> gets alt text: from the Sheet when it's there, otherwise a sensible
  default built from the row (and Content Check flags the missing alt text).

Most blocks are small pieces of HTML styled by style.py. Text from the Sheet is
always escaped before it goes into HTML, so a stray < or & can't break a page.
"""

from __future__ import annotations

import html

import streamlit as st

import config
from content import (
    TEAM_BOARDS,
    get_site_text,
    is_placeholder,
    mailto,
    photo_url,
    safe_url,
)

PAGES = {
    "home": "pages/home.py",
    "dogs": "pages/meet_the_dogs.py",
    "sponsor": "pages/sponsor_donate.py",
    "apply": "pages/apply.py",
    "involved": "pages/get_involved.py",
    "events": "pages/events.py",
    "news": "pages/news.py",
    "about": "pages/about.py",
    "faq": "pages/faq.py",
    "vest": "pages/respect_the_vest.py",
    "ask": "pages/ask_isd.py",
    "check": "pages/content_check.py",
}

# Relative links between pages (they work locally and on Streamlit Cloud).
HREF = {
    "home": "./", "dogs": "dogs", "sponsor": "donate", "apply": "apply", "involved": "get-involved",
    "events": "events", "news": "news", "about": "about", "faq": "faq", "vest": "respect-the-vest", "ask": "ask", "check": "content-check",
}


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

def text(key: str, default: str = "") -> str:
    """SiteText value, or default if it is blank or still a placeholder."""
    value = get_site_text(key)
    return default if is_placeholder(value) else value


def show(value) -> str:
    """A cell from any tab, or "" if it is blank or still a placeholder."""
    return "" if is_placeholder(value) else str(value)


def esc(value) -> str:
    return html.escape(str(value or ""))


def paras(value) -> str:
    """Sheet text -> HTML paragraphs (blank lines in the cell start a new paragraph)."""
    blocks = [b.strip() for b in str(value or "").split("\n\n") if b.strip()]
    return "".join(f"<p>{esc(b)}</p>" for b in blocks)


def md(value) -> str:
    """Make Sheet text safe for Streamlit markdown: a $ sign would otherwise start a math formula."""
    return str(value or "").replace("$", "\\$")


def say(value) -> None:
    st.markdown(md(value))


def nice_date(d) -> str:
    """Saturday, March 14, 2027 (works on every operating system)."""
    return f"{d:%A, %B} {d.day}, {d.year}"


def short_date(d) -> str:
    return f"{d:%B} {d.day}, {d.year}"


def html_block(markup: str) -> None:
    st.html(markup)


# --------------------------------------------------------------------------
# Links and buttons
# --------------------------------------------------------------------------

def btn(label: str, href: str, kind: str = "primary", external: bool = False) -> str:
    """A link styled as a button. Returns "" if the link isn't set yet."""
    if external:
        href = safe_url(href) or (href if str(href).startswith("mailto:") else "")
        if not href:
            return ""
        return (f'<a class="isd-btn isd-btn-{kind}" href="{esc(href)}" target="_blank" rel="noopener">'
                f'{esc(label)}<span class="isd-sr"> (opens in a new tab)</span></a>')
    return f'<a class="isd-btn isd-btn-{kind}" href="{esc(HREF.get(href, href))}" target="_self">{esc(label)}</a>'


def email_html(key: str) -> str:
    email = text(key)
    return f'<a href="{esc(mailto(email))}">{esc(email)}</a>' if mailto(email) else ""


def email_link(key: str) -> str:
    """Markdown link for a SiteText email key."""
    email = text(key)
    return f"[{email}]({mailto(email)})" if mailto(email) else ""


def link_button(label: str, url: str, *, primary: bool = False, key: str | None = None) -> bool:
    """Streamlit button that opens an outside link. Shows nothing if the link isn't set yet."""
    url = safe_url(url) or (url if str(url).startswith("mailto:") else "")
    if not url:
        return False
    st.link_button(label, url, type="primary" if primary else "secondary", width="stretch", key=key)
    return True


# --------------------------------------------------------------------------
# Page frame
# --------------------------------------------------------------------------

def header() -> None:
    logo = photo_url(text("logo_file"))
    logo_html = (f'<img src="{logo}" alt="Illini Service Dogs logo: an orange paw print in a blue circle">'
                 if logo else "")
    html_block(
        '<style>.isd-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;}</style>'
        f'<header class="isd-header">{logo_html}'
        f'<div><div class="isd-name">{esc(text("org_name", "Illini Service Dogs"))}</div>'
        f'<div class="isd-tagline">{esc(text("tagline"))}</div></div>'
        f'<div class="isd-spacer"></div>{btn("Donate", "sponsor")}</header>'
    )


def footer() -> None:
    contact = [esc(text("address"))] if text("address") else []
    if email_html("contact_email"):
        contact.append(email_html("contact_email"))
    if text("response_time"):
        contact.append(esc(text("response_time")))
    follow = []
    for key, label in (("instagram_url", "Illini Service Dogs on Instagram"),
                       ("facebook_url", "Illini Service Dogs on Facebook"),
                       ("amazon_wishlist_url", "Our Amazon Wishlist")):
        url = safe_url(get_site_text(key))
        if url:
            follow.append(f'<a href="{esc(url)}" target="_blank" rel="noopener">{label}'
                          f'<span class="isd-sr"> (opens in a new tab)</span></a>')
    html_block(
        '<footer class="isd-footer">'
        f'<div><div class="isd-foot-title">{esc(text("org_name", "Illini Service Dogs"))}</div>'
        f'{esc(text("tagline"))}<br>A 501(c)(3) not-for-profit organization.</div>'
        f'<div><div class="isd-foot-title">Contact</div>{"<br>".join(contact)}</div>'
        f'<div><div class="isd-foot-title">Follow and support</div>{"<br>".join(follow)}</div>'
        '<div class="isd-small">Content updated from ISD\'s Google Sheet. Photos © Illini Service Dogs.</div>'
        '</footer>'
    )


def hero(eyebrow: str, title: str, body: str, photo: str, alt: str, buttons: str = "") -> None:
    """Big top-of-page block with the page's h1, a paragraph, buttons and a photo."""
    url = photo_url(photo)
    img = f'<img src="{url}" alt="{esc(alt or "An Illini Service Dogs service dog in training")}">' if url else ""
    html_block(
        f'<section class="isd-hero"><div><div class="isd-eyebrow">{esc(eyebrow)}</div>'
        f'<h1>{esc(title)}</h1><p>{esc(body)}</p><div>{buttons}</div></div>'
        f'<div>{img}</div></section>'
    )


def page_head(title: str, intro: str = "") -> None:
    """The h1 for every page other than Home."""
    intro_html = f"<p>{esc(intro)}</p>" if intro else ""
    html_block(f'<section class="isd-pagehead"><h1>{esc(title)}</h1>{intro_html}</section>')


def section(title: str, lead: str = "") -> None:
    lead_html = f'<p class="isd-lead">{esc(lead)}</p>' if lead else ""
    html_block(f'<h2 class="isd-section-title">{esc(title)}</h2>{lead_html}')


def split(photo: str, alt: str, inner_html: str, *, reverse: bool = False) -> None:
    """Photo beside text. Stacks on phones."""
    url = photo_url(photo)
    img = f'<img src="{url}" alt="{esc(alt or "Illini Service Dogs photo")}" loading="lazy">' if url else ""
    a, b = (inner_html, img) if reverse else (img, inner_html)
    html_block(f'<div class="isd-split"><div>{a}</div><div>{b}</div></div>')


def callout(title: str, body: str, buttons: str = "") -> None:
    html_block(f'<section class="isd-callout"><h2>{esc(title)}</h2><p>{esc(body)}</p>{buttons}</section>')


# --------------------------------------------------------------------------
# Content blocks
# --------------------------------------------------------------------------

def stats() -> None:
    items = []
    for i in range(1, 5):
        number, _, label = text(f"stat_{i}").partition("|")
        if number.strip():
            items.append(f'<div class="isd-stat"><b>{esc(number.strip())}</b>{esc(label.strip())}</div>')
    if items:
        html_block(f'<div class="isd-stats">{"".join(items)}</div>')


def _img_or_placeholder(file: str, alt: str, name: str) -> str:
    url = photo_url(file)
    if url:
        return f'<img class="isd-photo" src="{url}" alt="{esc(alt)}" loading="lazy">'
    return (f'<div class="isd-placeholder" role="img" aria-label="Photo of {esc(name)} coming soon">'
            '🐾<br>Photo coming soon</div>')


def dog_card(dog: dict, *, sponsor: bool = True) -> str:
    name = dog["name"]
    alt = show(dog.get("alt_text")) or f"Photo of {name}, an Illini Service Dog"
    facts = " · ".join(f for f in (show(dog.get("breed")), show(dog.get("age"))) if f)
    stage = dog.get("training_stage")
    progress = ""
    if stage in config.TRAINING_STAGES:
        total = len(config.TRAINING_STAGES)
        label = f"Stage {stage} of {total}: {config.TRAINING_STAGES[stage]}"
        progress = (f'<div class="isd-meta">{esc(label)}</div><div class="isd-progress" role="progressbar" '
                    f'aria-valuemin="0" aria-valuemax="{total}" aria-valuenow="{stage}" aria-label="{esc(label)}">'
                    f'<span style="width:{stage / total * 100:.0f}%"></span></div>')
    tag = ('<span class="isd-tag">Graduate</span>' if dog.get("status") == "placed"
           else '<span class="isd-tag">In training</span>')
    actions = ""
    insta = safe_url(dog.get("instagram_url"))
    if insta:
        actions += (f'<a href="{esc(insta)}" target="_blank" rel="noopener">Follow {esc(name)} on Instagram'
                    f'<span class="isd-sr"> (opens in a new tab)</span></a><br>')
    if sponsor:
        own = safe_url(dog.get("sponsor_link"))
        actions += btn(f"Sponsor {name}", own, external=True) if own else btn(f"Sponsor {name}", "sponsor")
    facts_html = f'<div class="isd-meta">{esc(facts)}</div>' if facts else ""
    return (f'<article class="isd-card">{_img_or_placeholder(dog.get("photo_file"), alt, name)}'
            f'<div class="isd-body"><div>{tag}</div><h3>{esc(name)}</h3>{facts_html}'
            f'{paras(show(dog.get("bio")))}{progress}<div class="isd-actions">{actions}</div></div></article>')


def dogs_grid(dogs: list[dict], *, sponsor: bool = True) -> None:
    html_block(f'<div class="isd-grid">{"".join(dog_card(d, sponsor=sponsor) for d in dogs)}</div>')


def steps(items: list[str]) -> None:
    lis = []
    for item in items:
        title, _, detail = item.partition(":")
        lis.append(f"<li><b>{esc(title.strip())}</b>{esc(detail.strip())}</li>")
    html_block(f'<ol class="isd-steps">{"".join(lis)}</ol>')


def levels(rows: list[dict]) -> None:
    cards = []
    for i, r in enumerate(rows):
        featured = " isd-featured" if i == len(rows) - 1 else ""
        link = btn(f"Give {r['amount']}", r.get("payment_link", ""), external=True)
        cards.append(f'<div class="isd-level{featured}"><b>{esc(r["amount"])}</b>'
                     f'<div class="isd-meta">{esc(r["tier_name"])}</div><p>{esc(show(r["covers"]))}</p>{link}</div>')
    html_block(f'<div class="isd-levels">{"".join(cards)}</div>')


def people(rows: list[dict]) -> None:
    out = []
    for r in rows:
        url = photo_url(r.get("photo_file"))
        if url:
            alt = show(r.get("alt_text")) or f"Headshot of {r['name']}"
            face = f'<img src="{url}" alt="{esc(alt)}" loading="lazy">'
        else:
            initials = "".join(p[0] for p in r["name"].split()[:2]).upper()
            face = f'<span class="isd-initials" aria-hidden="true">{esc(initials)}</span>'
        out.append(f'<div class="isd-person">{face}<b>{esc(r["name"])}</b><span>{esc(show(r.get("role")))}</span></div>')
    html_block(f'<div class="isd-people">{"".join(out)}</div>')


def team_by_board(team: list[dict]) -> None:
    for board, title in TEAM_BOARDS.items():
        rows = [r for r in team if r["board"] == board]
        if rows:
            html_block(f'<h3>{esc(title)}</h3>')
            people(rows)


def logos(rows: list[dict]) -> None:
    out = []
    for r in rows:
        url = photo_url(r.get("logo_file"))
        inner = (f'<img src="{url}" alt="{esc(show(r.get("alt_text")) or r["name"] + " logo")}" loading="lazy">'
                 if url else esc(r["name"]))
        link = safe_url(r.get("link"))
        if link:
            out.append(f'<a class="isd-logo" href="{esc(link)}" target="_blank" rel="noopener">{inner}'
                       f'<span class="isd-sr"> (opens in a new tab)</span></a>')
        else:
            out.append(f'<div class="isd-logo">{inner}</div>')
    html_block(f'<div class="isd-logos">{"".join(out)}</div>')


def gallery(rows: list[dict]) -> None:
    figs = []
    for r in rows:
        url = photo_url(r.get("photo_file"))
        if not url:
            continue
        alt = show(r.get("alt_text")) or "Illini Service Dogs photo"
        cap = f'<figcaption>{esc(show(r.get("caption")))}</figcaption>' if show(r.get("caption")) else ""
        figs.append(f'<figure><img src="{url}" alt="{esc(alt)}" loading="lazy">{cap}</figure>')
    if figs:
        html_block(f'<div class="isd-gallery">{"".join(figs)}</div>')


def news_cards(rows: list[dict], *, teaser_only: bool = False) -> None:
    cards = []
    for r in rows:
        img = ""
        if photo_url(r.get("photo_file")):
            alt = show(r.get("alt_text")) or r["title"]
            img = f'<img class="isd-photo" src="{photo_url(r["photo_file"])}" alt="{esc(alt)}" loading="lazy">'
        body = show(r.get("body"))
        first = body.split("\n\n")[0]
        teaser = first if len(first) < 220 else first[:217].rsplit(" ", 1)[0] + "…"
        more = ""
        if teaser_only:
            more = f'<div class="isd-actions">{btn("Read the story", "news", kind="ghost")}</div>'
        elif body and body != teaser:
            more = f"<details><summary>Read the full story</summary>{paras(body)}</details>"
        cards.append(f'<article class="isd-card">{img}<div class="isd-body">'
                     f'<div class="isd-meta">{esc(short_date(r["date"]))}</div><h3>{esc(r["title"])}</h3>'
                     f'<p>{esc(teaser)}</p>{more}</div></article>')
    html_block(f'<div class="isd-news">{"".join(cards)}</div>')


def event_card(event: dict) -> str:
    when = nice_date(event["date"])
    if show(event.get("start_time")):
        when += f" at {event['start_time']}"
    where = f"<p><b>Where:</b> {esc(event['location'])}</p>" if show(event.get("location")) else ""
    link = btn(f"Details: {event['title']}", event.get("link", ""), kind="ghost", external=True)
    return (f'<article class="isd-card"><div class="isd-body"><div class="isd-meta">{esc(when)}</div>'
            f'<h3>{esc(event["title"])}</h3>{where}{paras(show(event.get("description")))}'
            f'<div class="isd-actions">{link}</div></div></article>')


def events_grid(events: list[dict]) -> None:
    html_block(f'<div class="isd-grid isd-grid-wide">{"".join(event_card(e) for e in events)}</div>')
