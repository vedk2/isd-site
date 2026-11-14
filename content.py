"""Loads all site content from ISD's Google Sheet, with backup/ as a safety net.

How it works, in order, for each Sheet tab:
1. Look up the tab's published CSV link (Streamlit secrets first, then config.py).
2. Download it (5 second limit). If that fails, or the tab is missing required
   columns, quietly use backup/<tab>.csv instead.
3. Clean every row: trim spaces, drop empty rows, fix types. A bad row is skipped
   and described in plain English for the Content Check page. Nothing here
   should ever crash a page.
4. Remember the result for 10 minutes (st.cache_data) so the Sheet is not
   downloaded on every click.

Pages should only use the get_* functions at the bottom of this file.
"""

from __future__ import annotations

import io
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Callable

import pandas as pd
import streamlit as st

import config

# --------------------------------------------------------------------------
# What each tab must look like
# --------------------------------------------------------------------------

FAQ_CATEGORIES = ("applying", "donating", "sponsoring", "volunteering", "puppy_raising", "general")
DOG_STATUSES = ("in_training", "placed", "retired")

# SiteText keys the pages look up. Missing ones are listed on Content Check.
SITE_TEXT_KEYS = (
    "org_name", "tagline", "hero_headline", "hero_subtext", "mission", "impact_line",
    "founding_story", "how_we_are_run", "donation_use",
    "contact_email", "donate_email", "applicants_email", "careers_email", "tech_email",
    "address", "facebook_url", "instagram_url",
    "paypal_url", "venmo_url", "amazon_wishlist_url", "check_payable_to", "tax_letter_note",
    "application_url", "puppy_raiser_form_url", "newsletter_url", "response_time",
    "apply_who_we_serve", "apply_eligibility", "apply_timing_note",
    "apply_step_1", "apply_step_2", "apply_step_3", "apply_step_4", "apply_step_5",
    "puppy_raiser_text", "student_membership_text", "volunteer_text", "partner_text",
    "events_empty_text", "chatbot_disclaimer",
)

# Keys that may be blank on purpose (the related section just hides).
SITE_TEXT_OPTIONAL = {"newsletter_url"}


@dataclass
class TabSpec:
    key: str            # internal name, also the secrets key
    sheet_name: str     # what board members see as the tab name in Google Sheets
    backup_file: str
    columns: tuple[str, ...]
    required: tuple[str, ...]   # columns that must exist for the live tab to be trusted
    clean_row: Callable[[dict], tuple[dict | None, str]]


@dataclass
class TabResult:
    key: str
    sheet_name: str
    rows: pd.DataFrame
    source: str                                    # "live", "backup" or "missing"
    notes: list[str] = field(default_factory=list)    # plain-English problems
    skipped: list[str] = field(default_factory=list)  # "Row 4: reason"


# --------------------------------------------------------------------------
# Small helpers (also used by pages)
# --------------------------------------------------------------------------

def is_placeholder(value) -> bool:
    """True if a cell is empty or still says something like [ISD to confirm]."""
    text = str(value or "").strip()
    return not text or any(marker.lower() in text.lower() for marker in config.PLACEHOLDER_MARKERS)


def safe_url(value) -> str:
    """Return the value if it is a real web link, otherwise ""."""
    text = str(value or "").strip()
    if is_placeholder(text):
        return ""
    if text.lower().startswith(("https://", "http://")) and " " not in text:
        return text
    return ""


def mailto(email: str) -> str:
    email = str(email or "").strip()
    return f"mailto:{email}" if "@" in email and " " not in email else ""


def parse_date(value) -> date | None:
    """Accept 2027-03-14, 3/14/2027, March 14, 2027 and a few other common forms."""
    text = str(value or "").strip()
    if not text:
        return None
    formats = (
        "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d",
        "%m/%d/%Y", "%m/%d/%y", "%B %d, %Y", "%b %d, %Y", "%A, %B %d, %Y",
    )
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def photo_path(photo_file) -> Path | None:
    """Return the image inside images/ if it exists. Only a bare file name is allowed."""
    name = Path(str(photo_file or "").strip()).name
    if not name or name.startswith("."):
        return None
    path = config.IMAGES_DIR / name
    if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"} and path.is_file():
        return path
    return None


# --------------------------------------------------------------------------
# Row cleaners: return (clean_row, "") or (None, "reason it was skipped")
# --------------------------------------------------------------------------

def _clean_dog(row: dict) -> tuple[dict | None, str]:
    if not row["name"]:
        return None, "the dog has no name"
    status = row["status"].lower().replace(" ", "_").replace("-", "_") or "in_training"
    if status not in DOG_STATUSES:
        return None, f'status "{row["status"]}" should be in_training, placed or retired'
    row["status"] = status
    try:
        stage = int(float(row["training_stage"]))
        row["training_stage"] = stage if stage in config.TRAINING_STAGES else None
    except ValueError:
        row["training_stage"] = None
    return row, ""


def _clean_faq(row: dict) -> tuple[dict | None, str]:
    if not row["question"]:
        return None, "the question is empty"
    if not row["answer"]:
        return None, f'"{row["question"]}" has an empty answer'
    category = row["category"].lower().replace(" ", "_").replace("-", "_")
    row["category"] = category if category in FAQ_CATEGORIES else "general"
    return row, ""


def _clean_event(row: dict) -> tuple[dict | None, str]:
    if not row["title"]:
        return None, "the event has no title"
    when = parse_date(row["date"])
    if when is None:
        shown = row["date"] or "(blank)"
        return None, f'"{row["title"]}" has a date we can\'t read: {shown}. Use YYYY-MM-DD, like 2027-03-14'
    row["date"] = when
    return row, ""


def _clean_tier(row: dict) -> tuple[dict | None, str]:
    if not row["tier_name"]:
        return None, "the tier has no name"
    try:
        row["sort_order"] = int(float(row["sort_order"]))
    except ValueError:
        row["sort_order"] = 999
    return row, ""


def _clean_site_text(row: dict) -> tuple[dict | None, str]:
    if not row["key"]:
        return None, "the key column is empty"
    row["key"] = row["key"].lower().replace(" ", "_")
    return row, ""


TABS: dict[str, TabSpec] = {
    spec.key: spec
    for spec in (
        TabSpec("dogs", "Dogs", "dogs.csv",
                ("name", "breed", "age", "bio", "training_stage", "photo_file", "alt_text",
                 "instagram_url", "sponsor_link", "status"),
                ("name", "status"), _clean_dog),
        TabSpec("faq", "FAQ", "faq.csv",
                ("question", "answer", "category", "keywords"),
                ("question", "answer"), _clean_faq),
        TabSpec("events", "Events", "events.csv",
                ("title", "date", "start_time", "location", "description", "link"),
                ("title", "date"), _clean_event),
        TabSpec("sponsor_tiers", "SponsorTiers", "sponsor_tiers.csv",
                ("tier_name", "amount", "covers", "payment_link", "sort_order"),
                ("tier_name", "amount"), _clean_tier),
        TabSpec("site_text", "SiteText", "site_text.csv",
                ("key", "value"),
                ("key", "value"), _clean_site_text),
    )
}


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def _parse_csv(text: str) -> pd.DataFrame:
    """Read CSV text as all-strings. Lines starting with # at the top are notes, not data."""
    lines = text.lstrip("﻿").splitlines()
    while lines and lines[0].lstrip().startswith("#"):
        lines.pop(0)
    df = pd.read_csv(io.StringIO("\n".join(lines)), dtype=str, keep_default_na=False)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df


def _fetch_text(url: str, timeout: float) -> str:
    if not url.lower().startswith(("https://", "http://")):
        raise ValueError("not a web link")
    request = urllib.request.Request(url, headers={"User-Agent": "isd-site"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8-sig")


def _clean(df: pd.DataFrame, spec: TabSpec, result: TabResult) -> pd.DataFrame:
    for col in spec.columns:
        if col not in df.columns:
            df[col] = ""
    df = df[list(spec.columns)].astype(str).apply(lambda s: s.str.strip())
    clean_rows = []
    for position, raw in enumerate(df.to_dict("records")):
        if not any(raw.values()):
            continue  # fully empty row: ignore without a warning
        try:
            row, reason = spec.clean_row(dict(raw))
        except Exception as exc:  # one strange row must never take the page down
            row, reason = None, f"unexpected problem ({exc})"
        if row is None:
            result.skipped.append(f"Row {position + 2}: {reason}")  # +2 = header row + 1-based
        else:
            clean_rows.append(row)
    return pd.DataFrame(clean_rows, columns=list(spec.columns), dtype=object)


def load_tab_uncached(key: str, url: str, backup_dir: Path | None = None,
                      timeout: float | None = None) -> TabResult:
    """Load one tab: live Sheet first, backup CSV if anything goes wrong. Never raises."""
    spec = TABS[key]
    backup_dir = backup_dir or config.BACKUP_DIR
    timeout = config.FETCH_TIMEOUT_SECONDS if timeout is None else timeout
    result = TabResult(key, spec.sheet_name, pd.DataFrame(columns=list(spec.columns)), "missing")

    raw = None
    if url:
        try:
            live = _parse_csv(_fetch_text(url, timeout))
            missing = [c for c in spec.required if c not in live.columns]
            if missing:
                result.notes.append(
                    f"The live {spec.sheet_name} tab is missing the column(s) "
                    f"{', '.join(missing)}, so the site is showing the backup copy instead.")
            else:
                raw, result.source = live, "live"
        except Exception:
            result.notes.append(
                f"Couldn't reach the Google Sheet for {spec.sheet_name}, "
                "so the site is showing the backup copy.")
    else:
        result.notes.append(f"No Google Sheet link is set for {spec.sheet_name}, so the site is using the backup copy.")

    if raw is None:
        try:
            raw = _parse_csv((backup_dir / spec.backup_file).read_text(encoding="utf-8-sig"))
            result.source = "backup"
        except Exception:
            result.notes.append(f"The backup file backup/{spec.backup_file} is missing or unreadable.")
            return result
        missing = [c for c in spec.required if c not in raw.columns]
        if missing:
            result.notes.append(f"backup/{spec.backup_file} is missing the column(s) {', '.join(missing)}.")

    result.rows = _clean(raw, spec, result)
    return result


def sheet_url(key: str) -> str:
    try:
        url = st.secrets["sheets"][key]
    except Exception:  # no secrets file, no [sheets] section, or no entry
        url = ""
    return str(url or config.SHEET_URLS.get(key, "")).strip()


@st.cache_data(ttl=config.CACHE_SECONDS, show_spinner=False)
def _load_cached(key: str, url: str) -> TabResult:
    return load_tab_uncached(key, url)


def load_tab(key: str) -> TabResult:
    # The link is part of the cache key, so changing a link (in config.py or in
    # Streamlit secrets) takes effect right away instead of after 10 minutes.
    return _load_cached(key, sheet_url(key))


def clear_cache() -> None:
    _load_cached.clear()


def load_all() -> dict[str, TabResult]:
    return {key: load_tab(key) for key in TABS}


# --------------------------------------------------------------------------
# What pages use
# --------------------------------------------------------------------------

def get_site_text_map() -> dict[str, str]:
    rows = load_tab("site_text").rows
    return {r["key"]: r["value"] for r in rows.to_dict("records")}


def get_site_text(key: str, default: str = "") -> str:
    value = get_site_text_map().get(key, "")
    return value if value else default


def get_dogs() -> pd.DataFrame:
    return load_tab("dogs").rows


def dogs_with_status(status: str) -> pd.DataFrame:
    dogs = get_dogs()
    return dogs[dogs["status"] == status]


def get_faq() -> pd.DataFrame:
    return load_tab("faq").rows


def get_sponsor_tiers() -> pd.DataFrame:
    tiers = load_tab("sponsor_tiers").rows
    return tiers.sort_values("sort_order", kind="stable") if not tiers.empty else tiers


def upcoming_events(events: pd.DataFrame, today: date | None = None) -> pd.DataFrame:
    """Events from today onward, soonest first. Past events disappear on their own."""
    today = today or date.today()
    if events.empty:
        return events
    keep = events[events["date"].apply(lambda d: d >= today)]
    return keep.sort_values("date", kind="stable")


def get_upcoming_events(today: date | None = None) -> pd.DataFrame:
    return upcoming_events(load_tab("events").rows, today)


def find_placeholders(results: dict[str, TabResult]) -> list[str]:
    """Every cell still waiting on ISD, as 'Dogs, Millie: breed'."""
    found = []
    for result in results.values():
        df = result.rows
        if df.empty:
            continue
        label_col = df.columns[0]
        for record in df.to_dict("records"):
            for col, value in record.items():
                if col == label_col or not isinstance(value, str) or not value:
                    continue
                if is_placeholder(value):
                    found.append(f"{result.sheet_name}, {record[label_col]}: {col}")
    return found
