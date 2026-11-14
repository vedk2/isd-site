# Illini Service Dogs website

A Streamlit site for [Illini Service Dogs](https://www.illiniservicedogs.com) (ISD), a UIUC nonprofit and student org that trains mobility service dogs and places them free of charge. Built as a BUS 401 Purpose Project by Ved Kulkarni and Nithin Raj (Fall 2026).

**Board members:** you don't need this file. Read [HANDOFF_GUIDE.md](HANDOFF_GUIDE.md) instead.

## The one design rule

All content (dogs, FAQ, events, sponsor tiers, every paragraph of site text) lives in **one Google Sheet owned by ISD**. The code only renders it. Board members who don't code update the Sheet, and the site picks up the change within 10 minutes. Change code only to add a feature.

Other rules the code follows:

- No payment processing. Donate and Sponsor buttons link out to ISD's PayPal, Venmo and Amazon.
- No personal data. Apply and Puppy Raiser link to ISD's own forms. There's no database, login, analytics or chat logging.
- No paid APIs or keys. The chatbot is plain TF-IDF matching against the FAQ tab.
- A Sheet cell that's blank or says `[ISD to confirm]` / `$XX` is hidden from visitors and listed on the Content Check page.

## Run it locally

Requires Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
streamlit run app.py
```

Open http://localhost:8501. With no Sheet links configured, the site runs entirely from `backup/`.

To test against the live Sheet, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste in the published CSV links. `secrets.toml` is git-ignored.

## Project layout

```
app.py              navigation, shared header and footer
config.py           Sheet link fallbacks, cache time, chatbot threshold, training stage names
content.py          loads + cleans every Sheet tab, falls back to backup/
chatbot.py          FAQ matcher (TF-IDF + cosine similarity)
ui.py               shared pieces: dog cards, event cards, buttons, header, footer
style.py            the only custom CSS (small, optional tweaks)
pages/              one file per page; pages only render content
backup/             CSV copy of every Sheet tab
images/             dog photos, referenced by file name from the Dogs tab
scripts/refresh_backup.py
tests/
.streamlit/config.toml           theme colors (the one place to change them)
.streamlit/secrets.toml.example  where the Sheet links go
```

## How content loading works

`content.py` handles each of the five tabs (`Dogs`, `FAQ`, `Events`, `SponsorTiers`, `SiteText`) the same way:

1. **Find the link.** Use `st.secrets["sheets"][<tab>]`, falling back to `config.SHEET_URLS`.
2. **Download it** with a 5 second timeout.
3. **Fall back** to `backup/<tab>.csv` if the download fails, the link is blank, or the tab is missing a required column. This happens silently, and the Content Check page explains it.
4. **Clean the rows.** Trim whitespace, drop fully empty rows, normalize values (status, category, dates, integers). A row that can't be used is skipped and recorded in plain English. One bad row never breaks a page.
5. **Cache** the result with `st.cache_data(ttl=600)`.

Pages call only the `get_*` helpers (`get_dogs()`, `get_faq()`, `get_upcoming_events()`, `get_site_text(key, default)`, ...). `get_site_text` never raises on a missing key.

Leading lines that start with `#` in a CSV are treated as notes and ignored. `backup/faq.csv` uses one to mark the FAQ as a draft for ISD to review.

### Sheet tabs and columns

| Tab | Columns | Notes |
|---|---|---|
| Dogs | name, breed, age, bio, training_stage, photo_file, alt_text, instagram_url, sponsor_link, status | stage is 1 to 4 (names in `config.TRAINING_STAGES`); status is in_training, placed or retired |
| FAQ | question, answer, category, keywords | category is applying, donating, sponsoring, volunteering, puppy_raising or general |
| Events | title, date, start_time, location, description, link | date is YYYY-MM-DD (M/D/YYYY also works); past events hide themselves |
| SponsorTiers | tier_name, amount, covers, payment_link, sort_order | tiers whose amount is a placeholder are hidden |
| SiteText | key, value, where_it_shows | `where_it_shows` is only a note for editors; the keys the app reads are in `content.SITE_TEXT_KEYS` |

## Refreshing the backup

The backup is what visitors see if Google is unreachable, so keep it reasonably fresh (every few months, or after big edits):

```bash
python scripts/refresh_backup.py
git add backup && git commit -m "Refresh content backup"
```

The script reads the links from `.streamlit/secrets.toml` and only overwrites a tab that downloads cleanly with the right columns.

## The chatbot

`chatbot.FaqMatcher` builds a TF-IDF matrix (word unigrams and bigrams, a small suffix stemmer, English stop words) over each FAQ row's question and keywords (weighted 3x) plus its answer. A visitor's question is matched by cosine similarity:

- If the score is at least `config.CHATBOT_THRESHOLD` (0.20), the bot shows the best answer and up to 3 related questions.
- Otherwise it says it isn't sure and gives the `contact_email` from SiteText.

The threshold was tuned in `tests/test_chatbot.py`. Real questions scored 0.22 or higher, and off-topic ones scored 0.18 or lower. If you change the FAQ a lot, rerun the tests. The usual fix for a missed question is adding words to that row's `keywords` cell, not changing code.

A paid LLM is deliberately not wired in. If ISD ever wants one, add it as an optional rephrasing step that only runs when a key exists in secrets and only rephrases the matched FAQ answer.

## Tests

```bash
pytest
```

- `test_content.py`: backup loads, bad or unreachable links fall back, missing columns don't crash, past events hide, empty and bad rows are handled.
- `test_chatbot.py`: 22 realistic questions reach the right FAQ entry, 6 off-topic ones fall below the threshold.
- `test_pages.py`: every page renders without errors (via `streamlit.testing.AppTest`), once with the placeholder seed content and once with fully filled-in content.

## Deploy (Streamlit Community Cloud, free)

1. Push this folder to a GitHub repo **owned by an ISD account** (for example the tech_support@ Google/GitHub login), not a student's personal account.
2. At https://share.streamlit.io, sign in with that GitHub account and choose **Create app**. Pick the repo, branch `main`, main file `app.py`, and Python 3.11 or newer.
3. Under **Advanced settings → Secrets**, paste the `[sheets]` block from `secrets.toml.example` with the real published CSV links.
4. Deploy. Every push to `main` redeploys automatically.

Changing a Sheet link later only takes an edit in **App → Settings → Secrets**, with no code change.

Free apps go to sleep after a stretch with no visitors and take a few seconds to wake up. Linking the site from illiniservicedogs.com keeps it busier.

## Connecting the Google Sheet

1. Create a Google Sheet in ISD's Google account with five tabs named exactly `Dogs`, `FAQ`, `Events`, `SponsorTiers`, `SiteText`.
2. For each tab, open **File → Import → Upload**, choose the matching file from `backup/`, and pick **Replace current sheet**.
3. Open **File → Share → Publish to web**. Choose a tab and **Comma-separated values (.csv)**, then click **Publish**. Copy the link. Repeat for all five tabs, since each tab gets its own link (the `gid=` part differs).
4. Put the five links into Streamlit secrets (see Deploy, step 3) or your local `.streamlit/secrets.toml`.
5. Open the Content Check page. All five tabs should say "loaded live".

Published links are read-only and public. That's fine because everything in the Sheet is already public website content. Never put private information in this Sheet.
