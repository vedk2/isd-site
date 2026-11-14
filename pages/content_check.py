"""A plain-English health report for board members. No code knowledge needed."""

from datetime import date

import streamlit as st

import ui
from content import (
    SITE_TEXT_KEYS,
    SITE_TEXT_OPTIONAL,
    find_placeholders,
    is_placeholder,
    load_all,
    load_tab,
    photo_path,
    upcoming_events,
)

st.title("Content Check")
ui.say("This page is for ISD board members. It shows whether the website is reading the Google Sheet "
       "and lists anything in the Sheet that needs fixing. Edits to the Sheet show up within about 10 minutes.")

if st.button("Check the Sheet again now", icon=":material/refresh:"):
    load_tab.clear()
    st.rerun()

results = load_all()


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
checklist(
    "Dogs missing a photo",
    [f"{d['name']}: no image named \"{d['photo_file'] or '(blank)'}\" in the images folder" for d in dogs
     if not photo_path(d["photo_file"])],
    "Every dog has a photo.",
)
checklist(
    "Dogs missing alt text (a short description of the photo for blind and low-vision visitors)",
    [d["name"] for d in dogs if is_placeholder(d["alt_text"])],
    "Every dog has alt text.",
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
