import streamlit as st

import ui
from content import dogs_with_status, get_upcoming_events

st.title(ui.md(ui.text("hero_headline", "Illini Service Dogs")))
if ui.text("hero_subtext"):
    ui.say(ui.text("hero_subtext"))

c1, c2, c3 = st.columns(3)
with c1:
    ui.go_button("Sponsor a Dog", "sponsor", key="home-sponsor")
with c2:
    ui.go_button("Donate", "sponsor", key="home-donate")
with c3:
    ui.go_button("Apply for a Service Dog", "apply", key="home-apply")

if ui.text("impact_line"):
    st.info(ui.md(ui.text("impact_line")), icon=":material/favorite:")

dogs = dogs_with_status("in_training").head(3).to_dict("records")
if dogs:
    st.header("Dogs in training")
    ui.grid(dogs, lambda d: ui.dog_card(d, key_prefix="home"))
    ui.go_button("Meet all the dogs", "dogs", primary=False, key="home-all-dogs")

events = get_upcoming_events()
if not events.empty:
    st.header("Next event")
    nxt = events.iloc[0].to_dict()
    ui.event_card(nxt)
    ui.go_button("See all events", "events", primary=False, key="home-events")

if ui.text("mission"):
    st.header("Our mission")
    ui.say(ui.text("mission"))
