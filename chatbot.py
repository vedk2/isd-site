"""Ask ISD: answers visitor questions from the FAQ tab. Free, no API keys.

How it works: every FAQ row (question + keywords + answer) is turned into a
TF-IDF word-weight vector. A visitor's question gets the same treatment, and we
pick the FAQ row whose vector points the most in the same direction (cosine
similarity, 0 = nothing in common, 1 = identical). If even the best match is
below config.CHATBOT_THRESHOLD, the bot says it isn't sure and gives the
contact email instead of guessing.

To improve answers, board members edit the FAQ tab (especially the keywords
column). No code changes needed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import config

# Words that appear in nearly every question here and say nothing about the topic.
_EXTRA_STOP = {"isd", "illini", "service", "dog", "dogs", "please", "want", "like", "know", "tell",
               "hi", "hello", "hey", "thanks", "thank", "does", "did", "doing", "done", "im", "ive",
               "dont", "cant", "wont", "use", "just", "really"}
_STOP = (ENGLISH_STOP_WORDS | _EXTRA_STOP) - {"how", "long", "who", "where", "cost", "free"}

_SUFFIXES = ("ications", "ication", "ions", "ion", "ings", "ing", "ers", "er", "ies", "ied", "ed", "es", "s")


def _stem(word: str) -> str:
    """Tiny suffix trimmer so 'donate', 'donating' and 'donation' all become 'donat'."""
    for _ in range(2):  # twice, so 'volunteering' -> 'volunteer' -> 'volunt'
        for suffix in _SUFFIXES:
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                word = word[: -len(suffix)] + ("y" if suffix in ("ies", "ied", "ication", "ications") else "")
                break
        else:
            break
    if word.endswith("e") and len(word) > 3:
        word = word[:-1]
    if word.endswith("y") and len(word) > 3:
        word = word[:-1] + "i"   # apply -> appli, applies -> appli
    return word


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", str(text).lower())
    return [_stem(w) for w in words if w not in _STOP and len(w) > 1]


@dataclass
class Match:
    question: str
    answer: str
    category: str
    score: float


class FaqMatcher:
    """Two signals, blended:
    - word match: TF-IDF over stemmed words (question + keywords count 3x, answer 1x)
    - fuzzy match: TF-IDF over 3-5 letter chunks of the question + keywords, so typos
      like "sponser" or "aply" still land near the right entry.
    """

    def __init__(self, faq: pd.DataFrame, threshold: float | None = None):
        self.faq = faq.reset_index(drop=True)
        self.threshold = config.CHATBOT_THRESHOLD if threshold is None else threshold
        self.suggest_threshold = config.CHATBOT_SUGGEST_THRESHOLD
        self.vectorizer = None
        if self.faq.empty:
            return
        docs = [f"{(r.question + ' ' + r.keywords + ' ') * 3}{r.answer}" for r in self.faq.itertuples()]
        self.vectorizer = TfidfVectorizer(tokenizer=tokenize, token_pattern=None, lowercase=False,
                                          ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform(docs)
        topics = [" ".join(tokenize(f"{r.question} {r.keywords}")) for r in self.faq.itertuples()]
        self.fuzzy = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        self.fuzzy_matrix = self.fuzzy.fit_transform(topics)

    def rank(self, question: str) -> list[Match]:
        words = tokenize(question)
        if self.vectorizer is None or not words:
            return []
        word_score = cosine_similarity(self.vectorizer.transform([question]), self.matrix)[0]
        fuzzy_score = cosine_similarity(self.fuzzy.transform([" ".join(words)]), self.fuzzy_matrix)[0]
        w = config.CHATBOT_FUZZY_WEIGHT
        scores = (1 - w) * word_score + w * fuzzy_score
        order = scores.argsort()[::-1]
        return [
            Match(self.faq.at[i, "question"], self.faq.at[i, "answer"], self.faq.at[i, "category"], float(scores[i]))
            for i in order
        ]

    def answer(self, question: str) -> tuple[Match | None, list[str]]:
        """Best match (or None if not confident) and up to 3 related FAQ questions."""
        ranked = self.rank(question)
        if not ranked or ranked[0].score < self.threshold:
            return None, []
        best = ranked[0]
        related = [m.question for m in ranked[1:] if m.score >= self.threshold / 2][:3]
        if len(related) < 3:  # top up with questions from the same topic
            same_topic = [q for q, c in zip(self.faq["question"], self.faq["category"])
                          if c == best.category and q != best.question and q not in related]
            related += same_topic[: 3 - len(related)]
        return best, related

    def suggestions(self, question: str, limit: int = 3) -> list[str]:
        """When the bot isn't confident: the closest FAQ questions, for a "Did you mean...?" list."""
        ranked = self.rank(question)
        if not ranked or ranked[0].score >= self.threshold:
            return []
        return [m.question for m in ranked[:limit] if m.score >= self.suggest_threshold]


_SMALL_TALK = {
    "greeting": re.compile(r"^(hi+|hello+|hey+|howdy|good (morning|afternoon|evening)|yo|sup|what'?s up)[\s!.?]*$"),
    "thanks": re.compile(r"^(thanks?( you)?( so much)?|thank you( so much)?|thx|ty|appreciate it|great,? thanks?)[\s!.?]*$"),
    "bye": re.compile(r"^(bye+|goodbye|see (you|ya)|later|that'?s all)[\s!.?]*$"),
    "bot": re.compile(r"^(who|what) are you\??$|^are you (a )?(bot|robot|real|human|ai)\??$"),
}


def small_talk(message: str) -> str:
    """"greeting", "thanks", "bye", "bot" or "" for a short social message."""
    text = message.strip().lower()
    for kind, pattern in _SMALL_TALK.items():
        if pattern.match(text):
            return kind
    return ""


def fallback_message(contact_email: str) -> str:
    email = contact_email or "ContactUs@illiniservicedogs.com"
    return (f"I'm not sure about that one. Email [{email}](mailto:{email}) "
            "and the team will get back to you.")
