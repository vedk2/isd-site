"""Illini Service Dogs website. Run with:  streamlit run app.py

This file only sets up navigation and the shared header/footer. Each page lives
in pages/, and all words, dogs, events and links come from the Google Sheet
(see content.py).
"""

import streamlit as st

import style
import ui

st.set_page_config(
    page_title="Illini Service Dogs",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="auto",
)
style.apply()

pages = [
    st.Page(ui.PAGES["home"], title="Home", icon=":material/home:", default=True),
    st.Page(ui.PAGES["dogs"], title="Meet the Dogs", icon=":material/pets:", url_path="dogs"),
    st.Page(ui.PAGES["sponsor"], title="Sponsor & Donate", icon=":material/volunteer_activism:", url_path="donate"),
    st.Page(ui.PAGES["apply"], title="Apply for a Service Dog", icon=":material/assignment:", url_path="apply"),
    st.Page(ui.PAGES["involved"], title="Get Involved", icon=":material/group_add:", url_path="get-involved"),
    st.Page(ui.PAGES["events"], title="Events", icon=":material/event:", url_path="events"),
    st.Page(ui.PAGES["about"], title="About", icon=":material/info:", url_path="about"),
    st.Page(ui.PAGES["ask"], title="Ask ISD", icon=":material/chat:", url_path="ask"),
    st.Page(ui.PAGES["check"], title="Content Check (board members)", icon=":material/fact_check:",
            url_path="content-check"),
]

current = st.navigation(pages, position="top")
ui.header()
current.run()
ui.footer()
