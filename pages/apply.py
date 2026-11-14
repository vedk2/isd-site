import streamlit as st

import ui
from content import get_site_text

st.title("Apply for a Service Dog")
st.header("Who we serve")
if ui.text("apply_who_we_serve"):
    ui.say(ui.text("apply_who_we_serve"))
if ui.text("apply_eligibility"):
    ui.say(ui.text("apply_eligibility"))

st.header("How it works")
steps = [ui.text(f"apply_step_{i}") for i in range(1, 6)]
steps = [s for s in steps if s]
for number, step in enumerate(steps, start=1):
    title, _, detail = step.partition(":")
    with st.container(border=True):
        ui.say(f"**Step {number} of {len(steps)}: {title.strip()}**")
        if detail.strip():
            ui.say(detail.strip())

if ui.text("apply_timing_note"):
    st.header("A note on timing")
    ui.say(ui.text("apply_timing_note"))

st.header("Ready to apply?")
if not ui.link_button("Open the ISD application form", get_site_text("application_url"), primary=True,
                      key="apply-form"):
    msg = "The online application link is being updated."
    if ui.email_link("applicants_email"):
        msg += f" In the meantime, email {ui.email_link('applicants_email')}."
    ui.say(msg)
st.caption("The form is hosted by ISD. This website doesn't collect or store any of your information.")

questions = []
if ui.email_link("applicants_email"):
    questions.append(f"Questions about your application or its status: {ui.email_link('applicants_email')}")
if ui.email_link("tech_email"):
    questions.append(f"Trouble with the form itself: {ui.email_link('tech_email')}")
if questions:
    st.subheader("Questions")
    for q in questions:
        ui.say(f"- {q}")
