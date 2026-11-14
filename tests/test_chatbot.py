import pandas as pd
import pytest

import config
from chatbot import FaqMatcher, fallback_message, tokenize
from content import load_tab_uncached

FAQ = load_tab_uncached("faq", "").rows

# (what a visitor might type, the FAQ question it should land on)
ON_TOPIC = [
    ("how do i apply for a service dog", "How do I get a service dog?"),
    ("Where's the application?", "How do I get a service dog?"),
    ("is there a fee to get a service dog", "How much does a service dog cost me? Does ISD charge a fee?"),
    ("is it free?", "How much does a service dog cost me? Does ISD charge a fee?"),
    ("do you train dogs for PTSD or anxiety", "Do you provide service dogs for psychiatric disabilities like PTSD, anxiety, depression or autism?"),
    ("how long is the waitlist", "How long is your waiting list?"),
    ("will I definitely get a dog if I'm accepted", "If my application is accepted, am I guaranteed a service dog?"),
    ("I live in California, can I still apply", "I live far from Champaign. Will you still work with me?"),
    ("I applied last month, any update on my application status?", "How do I check the status of my application?"),
    ("the form is broken and gives an error", "The application form isn't working. Who do I contact?"),
    ("can I give money with venmo", "How can I donate?"),
    ("what is my donation used for", "Where does my donation go?"),
    ("where do I mail a check", "Can I donate by check?"),
    ("do I get a tax receipt", "Will I get a receipt for my taxes?"),
    ("can I buy dog food from your amazon wish list", "Can I donate supplies instead of money?"),
    ("I want to sponsor Millie", "How do I sponsor a dog?"),
    ("what does a puppy raiser do", "What is a puppy raiser?"),
    ("can I foster a puppy at my apartment in Urbana", "How do I become a puppy raiser?"),
    ("how do I join as a UIUC student", "I'm a University of Illinois student. Can I join at any time?"),
    ("are you hiring volunteers? I have a resume", "Are there volunteer or leadership roles open?"),
    ("our club wants to co-host a fundraiser with you", "Can my RSO or group partner with ISD?"),
    ("how do I contact you", "How do I contact Illini Service Dogs?"),
    ("who founded ISD", "How and when did Illini Service Dogs start?"),
    ("is ISD a 501c3 nonprofit", "Is Illini Service Dogs a charitable organization?"),
    ("is it ok to pet a service dog", "Can I pet a service dog? What should I do when I meet one?"),
    ("what can a business legally ask about my service dog", "What questions can I legally ask someone about their service dog?"),
    ("what tasks do the dogs learn", "What tasks do ISD dogs learn?"),
    ("will you train my own dog", "Will you train my own dog to be my service dog?"),
]
OFF_TOPIC = [
    "what's the weather like in Chicago tomorrow",
    "who won the Illinois football game",
    "can you help me with my calculus homework",
    "best pizza near campus",
    "what time does the library close",
    "asdfgh qwerty",
]


@pytest.fixture(scope="module")
def bot():
    return FaqMatcher(FAQ)


@pytest.mark.parametrize("question,expected", ON_TOPIC)
def test_on_topic_questions_find_the_right_answer(bot, question, expected):
    best, related = bot.answer(question)
    ranked = bot.rank(question)[:3]
    assert best is not None, f"no confident answer; top 3: {[(m.question, round(m.score, 2)) for m in ranked]}"
    assert best.question == expected, f"top 3: {[(m.question, round(m.score, 2)) for m in ranked]}"
    assert len(related) <= 3 and best.question not in related


@pytest.mark.parametrize("question", OFF_TOPIC)
def test_off_topic_questions_fall_below_threshold(bot, question):
    best, related = bot.answer(question)
    top = bot.rank(question)[:1]
    assert best is None, f"answered with {top[0].question!r} at {top[0].score:.2f}"
    assert related == []


def test_threshold_leaves_a_margin(bot):
    """Every on-topic score clears the threshold and every off-topic score stays under it."""
    lowest_hit = min(bot.rank(q)[0].score for q, _ in ON_TOPIC)
    highest_miss = max((bot.rank(q)[0].score if bot.rank(q) else 0.0) for q in OFF_TOPIC)
    assert highest_miss < config.CHATBOT_THRESHOLD <= lowest_hit


def test_empty_faq_and_empty_question_do_not_crash():
    empty = FaqMatcher(pd.DataFrame(columns=["question", "answer", "category", "keywords"]))
    assert empty.answer("how do I apply") == (None, [])
    assert FaqMatcher(FAQ).answer("   ?!") == (None, [])


def test_fallback_uses_contact_email():
    assert "ContactUs@illiniservicedogs.com" in fallback_message("ContactUs@illiniservicedogs.com")
    assert "ContactUs@illiniservicedogs.com" in fallback_message("")


def test_tokenize_matches_word_forms():
    assert tokenize("donating")[0] == tokenize("donation")[0] == tokenize("donate")[0]
