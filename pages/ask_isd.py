"""Ask ISD chatbot page. Questions are never saved or logged anywhere."""

import streamlit as st

import ui
from chatbot import FaqMatcher, fallback_message
from content import get_faq, get_site_text

STARTERS = [
    "How do I apply for a dog?",
    "How can I sponsor a dog?",
    "How do I become a puppy raiser?",
    "Where does my donation go?",
]


@st.cache_resource(ttl=600, show_spinner=False)
def _matcher(faq_signature: str) -> FaqMatcher:
    return FaqMatcher(get_faq())


def matcher() -> FaqMatcher:
    faq = get_faq()
    # Rebuild only when the FAQ tab actually changes.
    return _matcher(str(pd_hash(faq)))


def pd_hash(df) -> int:
    return hash(tuple(map(tuple, df.astype(str).values.tolist())))


def ask(question: str) -> None:
    st.session_state.chat.append({"role": "user", "content": question})
    best, related = matcher().answer(question)
    if best is None:
        reply = {"role": "assistant", "content": fallback_message(get_site_text("contact_email")), "related": []}
    else:
        reply = {"role": "assistant", "content": ui.md(best.answer),
                 "matched": best.question, "related": related}
    st.session_state.chat.append(reply)


def queue(question: str) -> None:
    st.session_state.pending = question


ui.page_head("Ask ISD", ui.text("chatbot_disclaimer", "Answers come from ISD's FAQ, not a live person."))

if "chat" not in st.session_state:
    st.session_state.chat = []
if st.session_state.get("pending"):
    ask(st.session_state.pop("pending"))

if not st.session_state.chat:
    st.header("Try asking")
    cols = st.columns(2)
    for i, starter in enumerate(STARTERS):
        cols[i % 2].button(starter, key=f"starter-{i}", on_click=queue, args=(starter,), width="stretch")

for turn, message in enumerate(st.session_state.chat):
    with st.chat_message(message["role"], avatar=":material/pets:" if message["role"] == "assistant" else None):
        if message["role"] == "user":
            st.markdown(ui.md(message["content"]))
        else:
            if message.get("matched"):
                st.caption(f"From the FAQ: {ui.md(message['matched'])}")
            st.markdown(message["content"])
            if message.get("related") and turn == len(st.session_state.chat) - 1:
                st.caption("Related questions")
                for j, related in enumerate(message["related"]):
                    st.button(related, key=f"related-{turn}-{j}", on_click=queue, args=(related,))

if st.session_state.chat:
    st.button("Start over", icon=":material/restart_alt:", on_click=lambda: st.session_state.update(chat=[]))

question = st.chat_input("Type your question about ISD")
if question:
    ask(question)
    st.rerun()
