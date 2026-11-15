"""Ask ISD chatbot page. Questions are never saved or logged anywhere."""

import chat_ui
import ui

ui.page_head("Ask ISD", ui.text("chatbot_disclaimer", "Answers come from ISD's FAQ, not a live person."))
chat_ui.render("page")
