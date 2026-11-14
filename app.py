"""Illini Service Dogs website. Run with:  streamlit run app.py

This file only sets up navigation and the shared header/footer. Each page lives
in pages/, and all words, dogs, events, photos and links come from the Google
Sheet (see content.py) and the static/images folder.
"""

import streamlit as st

import style
import ui

st.set_page_config(
    page_title="Illini Service Dogs",
    page_icon="static/images/isd-logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)
style.apply()

P = ui.PAGES
nav = {
    "": [
        st.Page(P["home"], title="Home", icon=":material/home:", default=True),
        st.Page(P["dogs"], title="Meet the Dogs", icon=":material/pets:", url_path="dogs"),
        st.Page(P["sponsor"], title="Sponsor & Donate", icon=":material/volunteer_activism:", url_path="donate"),
        st.Page(P["apply"], title="Apply for a Dog", icon=":material/assignment:", url_path="apply"),
        st.Page(P["involved"], title="Get Involved", icon=":material/group_add:", url_path="get-involved"),
    ],
    "About": [
        st.Page(P["about"], title="About ISD", icon=":material/info:", url_path="about"),
        st.Page(P["news"], title="News", icon=":material/newspaper:", url_path="news"),
        st.Page(P["events"], title="Events", icon=":material/event:", url_path="events"),
        st.Page(P["vest"], title="Respect the Vest", icon=":material/front_hand:", url_path="respect-the-vest"),
        st.Page(P["faq"], title="FAQ", icon=":material/help:", url_path="faq"),
        st.Page(P["ask"], title="Ask ISD (chat)", icon=":material/chat:", url_path="ask"),
        st.Page(P["check"], title="Content Check (board members)", icon=":material/fact_check:",
                url_path="content-check"),
    ],
}

current = st.navigation(nav, position="top")
ui.header()
current.run()
ui.footer()
