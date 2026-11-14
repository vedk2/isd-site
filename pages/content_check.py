"""A plain-English health report for board members. No code knowledge needed."""

from datetime import date

import streamlit as st

import config
import ui
from content import (
    SITE_TEXT_KEYS,
    SITE_TEXT_OPTIONAL,
    find_placeholders,
    clear_cache,
    is_placeholder,
    load_all,
    photo_path,
    upcoming_events,
)

ui.page_head("Content Check", "For ISD board members: whether the website is reading the Google Sheet, and anything "
             "in the Sheet that needs fixing. Edits to the Sheet show up within about 10 minutes.")

c1, c2 = st.columns(2)
with c1:
    if st.button("Check the Sheet again now", icon=":material/refresh:", width="stretch"):
        clear_cache()
        st.rerun()
with c2:
    st.link_button("Open the Google Sheet", config.SHEET_EDIT_URL, icon=":material/table:", width="stretch")

results = load_all()
oldest = min(r.loaded_at for r in results.values())
try:
    from zoneinfo import ZoneInfo
    t = oldest.astimezone(ZoneInfo("America/Chicago"))
    stamp = f"{t.hour % 12 or 12}:{t:%M %p} Central on {t:%b} {t.day}"
except Exception:
    stamp = oldest.strftime("%H:%M UTC")
st.caption(f"Content last loaded at {stamp}. The site re-reads the Sheet every 10 minutes.")


def checklist(title: str, items: list[str], ok_text: str) -> None:
    st.subheader(title)
    if items:
        st.warning(f"{len(items)} to fix", icon=":material/warning:")
        for item in items:
            ui.say(f"- {item}")
    else:
        st.success(ok_text, icon=":material/check_circle:")


# ---- 1. Where each tab came from -------------------------------------------
st.header("1. Is the site reading the Google Sheet?")
for result in results.values():
    count = f"{len(result.rows)} row" + ("" if len(result.rows) == 1 else "s")
    if result.source == "live":
        st.success(f"**{result.sheet_name}** tab: loaded live from the Google Sheet ({count}).",
                   icon=":material/cloud_done:")
    elif result.source == "backup":
        st.warning(f"**{result.sheet_name}** tab: showing the backup copy ({count}).",
                   icon=":material/cloud_off:")
    else:
        st.error(f"**{result.sheet_name}** tab: nothing could be loaded.", icon=":material/error:")
    for note in result.notes:
        st.caption(note)

# ---- 2. Rows skipped --------------------------------------------------------
st.header("2. Problems in the Sheet")
skipped = [f"{r.sheet_name} tab, {s}" for r in results.values() for s in r.skipped]
checklist("Rows the site skipped", skipped, "No rows were skipped.")

dogs = results["dogs"].rows.to_dict("records")
# (tab, column with the photo file, column naming the row, is a photo required?)
PHOTO_COLUMNS = [("dogs", "photo_file", "name", True), ("news", "photo_file", "title", False),
                 ("team", "photo_file", "name", False), ("gallery", "photo_file", "photo_file", True),
                 ("sponsors", "logo_file", "name", False)]
missing_photo, missing_alt = [], []
for tab, col, label, required in PHOTO_COLUMNS:
    for row in results[tab].rows.to_dict("records"):
        file = row[col]
        if file and not photo_path(file):
            missing_photo.append(f"{results[tab].sheet_name} tab, {row[label]}: no file named \"{file}\" "
                                 "in the static/images folder on GitHub")
        elif not file and required:
            missing_photo.append(f"{results[tab].sheet_name} tab, {row[label]}: the photo column is blank")
        alt_col = "alt_text"
        if file and photo_path(file) and is_placeholder(row.get(alt_col)) and tab != "sponsors":
            missing_alt.append(f"{results[tab].sheet_name} tab, {row[label]}")
checklist("Photos that can't be found", missing_photo, "Every photo listed in the Sheet was found.")
checklist(
    "Photos missing alt text (a short description of the photo for blind and low-vision visitors)",
    missing_alt,
    "Every photo has alt text.",
)
checklist(
    "Dogs with a training stage that isn't 1, 2, 3 or 4",
    [d["name"] for d in dogs if d["status"] == "in_training" and d["training_stage"] is None],
    "Every dog in training has a stage.",
)

event_problems = [s for s in results["events"].skipped]
checklist("Events with a date the site can't read", event_problems, "All event dates look good.")
events = results["events"].rows
hidden = len(events) - len(upcoming_events(events, date.today()))
if hidden:
    st.caption(f"{hidden} past event(s) are hidden automatically. You can delete them from the Sheet whenever you like.")

checklist("FAQ entries with an empty answer", [s for s in results["faq"].skipped], "Every FAQ question has an answer.")

text_keys = set(results["site_text"].rows["key"]) if not results["site_text"].rows.empty else set()
checklist(
    "SiteText keys that are missing",
    [f"{k} (add a row with this exact key)" for k in SITE_TEXT_KEYS if k not in text_keys and k not in SITE_TEXT_OPTIONAL],
    "All SiteText keys are present.",
)

# ---- 3. Placeholders --------------------------------------------------------
st.header("3. Still waiting on ISD")
ui.say("These cells are blank or still say [ISD to confirm] or $XX. Visitors don't see them until they're filled in.")
placeholders = find_placeholders(results)
site_text = results["site_text"].rows
placeholders += [f"SiteText, {r['key']}: value is blank" for r in site_text.to_dict("records")
                 if not r["value"] and r["key"] not in SITE_TEXT_OPTIONAL]
if placeholders:
    with st.expander(f"Show all {len(placeholders)} cells to fill in"):
        for item in placeholders:
            ui.say(f"- {item}")
else:
    st.success("Nothing is waiting on ISD.", icon=":material/check_circle:")
