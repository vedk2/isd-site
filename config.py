"""Settings that rarely change.

The Google Sheet links below are the defaults. A Streamlit secret with the same
name (see .streamlit/secrets.toml.example) overrides them, so a link can be
changed from the Streamlit Cloud dashboard without touching code. If a link is
blank or broken, the site uses backup/ instead.
"""

from pathlib import Path

ROOT = Path(__file__).parent
BACKUP_DIR = ROOT / "backup"
IMAGES_DIR = ROOT / "images"

# ISD's content Sheet: https://docs.google.com/spreadsheets/d/1dn6-9QMwlQ5c0LjPRj3ccA8jU-TPiEVQ0wwHkWJNUWY/edit
# Each link downloads one tab as CSV. The Sheet is shared "Anyone with the link: Viewer".
# A Streamlit secret with the same name overrides these (see secrets.toml.example).
_SHEET = "https://docs.google.com/spreadsheets/d/1dn6-9QMwlQ5c0LjPRj3ccA8jU-TPiEVQ0wwHkWJNUWY/export?format=csv&gid="
SHEET_URLS = {
    "dogs": _SHEET + "914704615",
    "faq": _SHEET + "1304248444",
    "events": _SHEET + "305217368",
    "sponsor_tiers": _SHEET + "840687152",
    "site_text": _SHEET + "1534344510",
}

# How long (seconds) the site remembers the Sheet before checking for edits.
CACHE_SECONDS = 600

# How long (seconds) to wait for Google before falling back to backup/.
FETCH_TIMEOUT_SECONDS = 5

# Chatbot: how similar a question must be to an FAQ entry to answer it (0 to 1).
# Lower = answers more questions but guesses more often. Tuned in tests/test_chatbot.py:
# real questions scored 0.22 or higher, off-topic ones 0.18 or lower.
CHATBOT_THRESHOLD = 0.20

# Any cell containing one of these is treated as "not filled in yet".
PLACEHOLDER_MARKERS = ("[ISD to confirm", "$XX")  # matches "[ISD to confirm]" and "[ISD to confirm: ...]"

TRAINING_STAGES = {
    1: "Puppy basics",
    2: "Public access",
    3: "Advanced mobility tasks",
    4: "Ready for placement",
}
