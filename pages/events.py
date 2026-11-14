import streamlit as st

import ui
from content import get_site_text, get_upcoming_events

st.title("Events")

events = get_upcoming_events().to_dict("records")
if events:
    for position, event in enumerate(events):
        ui.event_card({**event, "_pos": position}, heading_level="header")
else:
    ui.say(ui.text("events_empty_text", "No upcoming events right now. Follow us on Instagram for updates."))
    ui.link_button("Illini Service Dogs on Instagram", get_site_text("instagram_url"), key="events-insta")
