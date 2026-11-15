"""The Ask ISD chat, used by both the Ask ISD page and the pop-up on every other page.

Both share one conversation (st.session_state.chat), so a visitor can start a
question in the pop-up and keep going on the full page. Nothing typed here is
saved or logged anywhere; the conversation disappears when the tab is closed.
"""

from __future__ import annotations

import streamlit as st

import ui
from chatbot import FaqMatcher, fallback_message, small_talk
from content import get_faq, get_site_text

STARTERS = [
    "How do I apply for a dog?",
    "How can I sponsor a dog?",
    "How do I become a puppy raiser?",
    "Where does my donation go?",
]


@st.cache_resource(ttl=600, show_spinner=False)
def _matcher(faq_signature: int) -> FaqMatcher:
    return FaqMatcher(get_faq())


def matcher() -> FaqMatcher:
    faq = get_faq()
    # Rebuild only when the FAQ tab actually changes.
    return _matcher(hash(tuple(map(tuple, faq.astype(str).values.tolist()))))


# Where to send people for more after an answer, by FAQ category: (page, button label).
MORE = {
    "applying": ("apply", "Apply for a service dog"),
    "service_dogs": ("faq", "Read the full FAQ"),
    "etiquette": ("vest", "Respect the Vest"),
    "donating": ("sponsor", "Ways to give"),
    "sponsoring": ("sponsor", "Sponsor a dog"),
    "puppy_raising": ("involved", "Puppy raiser program"),
    "volunteering": ("involved", "Get involved"),
    "about_isd": ("about", "About ISD"),
    "general": ("about", "About ISD"),
}

SMALL_TALK = {  # SiteText key, fallback wording
    "greeting": ("chatbot_greeting", "Hi! I can answer questions about applying for a service dog, donating, "
                 "sponsoring, puppy raising and volunteering with ISD. What would you like to know?"),
    "thanks": ("chatbot_thanks", "You're welcome! Anything else I can help with?"),
    "bye": ("chatbot_bye", "Thanks for stopping by, and thank you for supporting Illini Service Dogs!"),
    "bot": ("chatbot_about", "I'm ISD's FAQ helper. I'm not a live person: I match your question to answers "
            "from ISD's FAQ. For anything else, email us."),
}


def ask(question: str) -> None:
    st.session_state.chat.append({"role": "user", "content": question})
    kind = small_talk(question)
    if kind:
        key, default = SMALL_TALK[kind]
        st.session_state.chat.append({"role": "assistant", "content": ui.md(ui.text(key, default))})
        return
    bot = matcher()
    best, related = bot.answer(question)
    if best is not None:
        reply = {"role": "assistant", "content": ui.md(best.answer), "matched": best.question,
                 "related": related, "more": MORE.get(best.category)}
    elif suggestions := bot.suggestions(question):
        email = get_site_text("contact_email") or "ContactUs@illiniservicedogs.com"
        reply = {"role": "assistant", "suggestions": suggestions,
                 "content": f"I'm not sure I understood. Did you mean one of these? "
                            f"If not, email [{email}](mailto:{email})."}
    else:
        reply = {"role": "assistant", "content": fallback_message(get_site_text("contact_email"))}
    st.session_state.chat.append(reply)


def _queue(question: str) -> None:
    st.session_state.chat_pending = question


def _submitted(key: str) -> None:
    question = st.session_state.get(key)
    if question:
        st.session_state.chat_pending = question


def _clear() -> None:
    st.session_state.chat = []


def render(prefix: str, *, compact: bool = False) -> None:
    """Draw the conversation, starter questions and input box. `prefix` keeps widget keys unique."""
    if "chat" not in st.session_state:
        st.session_state.chat = []
    if st.session_state.get("chat_pending"):
        ask(st.session_state.pop("chat_pending"))

    chat = st.session_state.chat
    if not chat:
        if compact:
            st.caption("Try asking")
            for i, starter in enumerate(STARTERS):
                st.button(starter, key=f"{prefix}-starter-{i}", on_click=_queue, args=(starter,), width="stretch")
        else:
            st.header("Try asking")
            cols = st.columns(2)
            for i, starter in enumerate(STARTERS):
                cols[i % 2].button(starter, key=f"{prefix}-starter-{i}", on_click=_queue, args=(starter,),
                                   width="stretch")

    for turn, message in enumerate(chat):
        avatar = ":material/pets:" if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            if message["role"] == "user":
                st.markdown(ui.md(message["content"]))
                continue
            if message.get("matched"):
                st.caption(f"From the FAQ: {ui.md(message['matched'])}")
            st.markdown(message["content"])
            latest = turn == len(chat) - 1
            if message.get("more"):
                page, label = message["more"]
                st.page_link(ui.PAGES[page], label=label, icon=":material/arrow_forward:")
            if message.get("suggestions") and latest:
                for j, option in enumerate(message["suggestions"]):
                    st.button(option, key=f"{prefix}-suggest-{turn}-{j}", on_click=_queue, args=(option,),
                              icon=":material/help:")
            if message.get("related") and latest:
                st.caption("Related questions")
                for j, related in enumerate(message["related"]):
                    st.button(related, key=f"{prefix}-related-{turn}-{j}", on_click=_queue, args=(related,))

    if chat:
        st.button("Start over", icon=":material/restart_alt:", key=f"{prefix}-clear", on_click=_clear)

    # The callback runs before the next redraw, so the new question shows up immediately.
    st.chat_input("Type your question about ISD", key=f"{prefix}-input", on_submit=_submitted, args=(f"{prefix}-input",))


@st.fragment
def floating() -> None:
    """The pop-up chat pinned to the bottom-right corner (positioned by style.py)."""
    with st.container(key="isd-chat-fab"):
        with st.popover("Ask ISD", icon=":material/chat:", type="primary"):
            st.markdown(f"**Ask ISD** · {ui.md(ui.text('chatbot_disclaimer', 'Answers come from ISD’s FAQ.'))}")
            render("pop", compact=True)
