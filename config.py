"""Settings that rarely change.

The Google Sheet links normally live in Streamlit secrets (see
.streamlit/secrets.toml.example) so they can be changed from the Streamlit Cloud
dashboard without touching code. The constants below are only used when no
secret is set. Leaving them blank is fine: the site then uses backup/.
"""

from pathlib import Path

ROOT = Path(__file__).parent
BACKUP_DIR = ROOT / "backup"
IMAGES_DIR = ROOT / "images"

# Fallback "Publish to web -> CSV" links, one per Sheet tab.
SHEET_URLS = {
    "dogs": "",
    "faq": "",
    "events": "",
    "sponsor_tiers": "",
    "site_text": "",
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
