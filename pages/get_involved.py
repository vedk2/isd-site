import streamlit as st

import ui
from content import get_site_text, safe_url

st.title("Get Involved")

st.header("Become a puppy raiser")
if ui.text("puppy_raiser_text"):
    ui.say(ui.text("puppy_raiser_text"))
if not ui.link_button("Open the Puppy Raiser form", get_site_text("puppy_raiser_form_url"), primary=True,
                      key="puppy-form"):
    if ui.email_link("contact_email"):
        ui.say(f"The Puppy Raiser form link is being updated. Email {ui.email_link('contact_email')} to ask about raising a puppy.")

st.header("UIUC students")
if ui.text("student_membership_text"):
    ui.say(ui.text("student_membership_text"))

st.header("Volunteer roles")
if ui.text("volunteer_text"):
    ui.say(ui.text("volunteer_text"))
if ui.email_link("careers_email"):
    ui.say(f"Send your resume to {ui.email_link('careers_email')}.")

st.header("Partner with us")
if ui.text("partner_text"):
    ui.say(ui.text("partner_text"))
if ui.email_link("contact_email"):
    ui.say(f"To plan something together, email {ui.email_link('contact_email')}.")

if safe_url(get_site_text("newsletter_url")):
    st.header("Stay in the loop")
    ui.link_button("Sign up for our newsletter", get_site_text("newsletter_url"), primary=True, key="newsletter")
