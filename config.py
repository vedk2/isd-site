"""Settings that rarely change.

The Google Sheet links below are the defaults. A Streamlit secret with the same
name (see .streamlit/secrets.toml.example) overrides them, so a link can be
changed from the Streamlit Cloud dashboard without touching code. If a link is
blank or broken, the site uses backup/ instead.
"""

from pathlib import Path

ROOT = Path(__file__).parent
BACKUP_DIR = ROOT / "backup"
IMAGES_DIR = ROOT / "static" / "images"  # served at app/static/images/ (see .streamlit/config.toml)

# ISD's content Sheet: https://docs.google.com/spreadsheets/d/1ivz6uGEAkoSfOUGJb7VPgHiHCoCm7T0-rO1-WGnRxgo/edit
# Each link downloads one tab as CSV. The Sheet is shared "Anyone with the link: Viewer".
# A Streamlit secret with the same name overrides these (see secrets.toml.example).
SHEET_EDIT_URL = "https://docs.google.com/spreadsheets/d/1ivz6uGEAkoSfOUGJb7VPgHiHCoCm7T0-rO1-WGnRxgo/edit"
_SHEET = "https://docs.google.com/spreadsheets/d/1ivz6uGEAkoSfOUGJb7VPgHiHCoCm7T0-rO1-WGnRxgo/export?format=csv&gid="
SHEET_URLS = {
    "dogs": _SHEET + "1683272492",
    "faq": _SHEET + "1746364396",
    "events": _SHEET + "1013601496",
    "sponsor_tiers": _SHEET + "1443989448",
    "site_text": _SHEET + "2043619265",
    "news": _SHEET + "1304260814",
    "team": _SHEET + "374141784",
    "sponsors": _SHEET + "1098584528",
    "gallery": _SHEET + "1915103294",
    "roles": _SHEET + "1618341177",
}

# How long (seconds) the site remembers the Sheet before checking for edits.
CACHE_SECONDS = 600

# How long (seconds) to wait for Google before falling back to backup/.
FETCH_TIMEOUT_SECONDS = 5

# Chatbot: how similar a question must be to an FAQ entry (0 to 1).
# At or above CHATBOT_THRESHOLD the bot answers. Between the two thresholds it says it isn't
# sure and offers "Did you mean...?" buttons. Below CHATBOT_SUGGEST_THRESHOLD it just gives
# the contact email. Tuned in tests/test_chatbot.py: real questions scored 0.27 or higher,
# typos 0.14 to 0.26, off-topic test questions 0.19 or lower.
CHATBOT_THRESHOLD = 0.25
CHATBOT_SUGGEST_THRESHOLD = 0.12
# How much the typo-tolerant letter matching counts, versus whole-word matching.
CHATBOT_FUZZY_WEIGHT = 0.3

# Any cell containing one of these is treated as "not filled in yet".
PLACEHOLDER_MARKERS = ("[ISD to confirm", "$XX")  # matches "[ISD to confirm]" and "[ISD to confirm: ...]"

TRAINING_STAGES = {
    1: "Puppy basics",
    2: "Public access",
    3: "Advanced mobility tasks",
    4: "Ready for placement",
}
