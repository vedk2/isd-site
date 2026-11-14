import streamlit as st

import ui
from content import FAQ_CATEGORIES, get_faq

ui.page_head("Frequently Asked Questions", ui.text("faq_intro", "Can't find your answer? Try Ask ISD, or email us."))
faq = get_faq()
if faq.empty:
    ui.say("The FAQ is being updated.")
for category, title in FAQ_CATEGORIES.items():
    rows = faq[faq["category"] == category].to_dict("records")
    if not rows:
        continue
    ui.section(title)
    for r in rows:
        with st.expander(r["question"]):
            ui.say(r["answer"].replace("\n", "  \n"))
ui.html_block(ui.btn("Ask ISD a question", "ask") + ui.btn("Email us", "mailto:" + ui.text("contact_email"), kind="ghost", external=True))
