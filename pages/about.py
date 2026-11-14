import streamlit as st

import ui

st.title("About Illini Service Dogs")

if ui.text("mission"):
    st.header("Our mission")
    ui.say(ui.text("mission"))

if ui.text("founding_story"):
    st.header("Our story")
    ui.say(ui.text("founding_story"))

if ui.text("how_we_are_run"):
    st.header("How ISD is run")
    ui.say(ui.text("how_we_are_run"))

if ui.email_link("contact_email"):
    st.header("Contact us")
    ui.say(f"Email {ui.email_link('contact_email')}.")
