# Illini Service Dogs website

A Streamlit site for [Illini Service Dogs](https://www.illiniservicedogs.com) (ISD), a UIUC nonprofit and student org that trains mobility service dogs and places them free of charge. Built as a BUS 401 Purpose Project by Ved Kulkarni and Nithin Raj (Fall 2026).

**Live site:** https://illini-service-dogs.streamlit.app (Streamlit Community Cloud, deployed from `main`, Python 3.11)

**Content Sheet:** [ISD Website Content](https://docs.google.com/spreadsheets/d/1ivz6uGEAkoSfOUGJb7VPgHiHCoCm7T0-rO1-WGnRxgo/edit)

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

Open http://localhost:8501. The site reads ISD's live Sheet using the links in `config.SHEET_URLS`. If Google is unreachable, it uses `backup/`.

To point at a different Sheet without editing code, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and change the links there. `secrets.toml` is git-ignored.

## Project layout

```
app.py              navigation, shared header and footer
config.py           Sheet link fallbacks, cache time, chatbot threshold, training stage names
content.py          loads + cleans every Sheet tab, falls back to backup/
chatbot.py          FAQ matcher (TF-IDF + cosine similarity)
chat_ui.py          the chat itself: the Ask ISD page and the pop-up pinned bottom-right on every other page
                    (one shared conversation; nothing typed is saved)
ui.py               shared HTML blocks: hero, cards, grids, people, logos, gallery, header, footer
style.py            all custom CSS (fonts, cards, grids, mobile layout) in one place
static/fonts/       Nunito heading font, hosted with the site (no Google Fonts request)
pages/              one file per page (Home, Meet the Dogs, Sponsor & Donate, Apply, Get Involved,
                    About, News, Events, Respect the Vest, FAQ, Ask ISD, Content Check); pages only render content
backup/             CSV copy of every Sheet tab
static/images/      every photo and logo, referenced by file name from the Sheet
                    (served at app/static/images/ because server.enableStaticServing is on)
scripts/refresh_backup.py
tests/
.streamlit/config.toml           theme colors (the one place to change them)
.streamlit/secrets.toml.example  optional override for the Sheet links
```

## How content loading works

`content.py` handles each of the five tabs (`Dogs`, `FAQ`, `Events`, `SponsorTiers`, `SiteText`) the same way:

1. **Find the link.** Use `st.secrets["sheets"][<tab>]`, falling back to `config.SHEET_URLS`.
2. **Download it** with a 5 second timeout.
3. **Fall back** to `backup/<tab>.csv` if the download fails, the link is blank, or the tab is missing a required column. This happens silently, and the Content Check page explains it.
4. **Clean the rows.** Trim whitespace, drop fully empty rows, normalize values (status, category, dates, integers). A row that can't be used is skipped and recorded in plain English. One bad row never breaks a page.
5. **Cache** the result with `st.cache_data(ttl=600)`.

Pages call only the `get_*` helpers (`get_dogs()`, `get_faq()`, `get_upcoming_events()`, `get_site_text(key, default)`, ...). `get_site_text` never raises on a missing key.

If a SiteText key is missing from the live Sheet, `get_site_text` uses the value from `backup/site_text.csv`, so a code update that adds a key never shows blank text. Page code also passes a fallback for its intro text.

Leading lines that start with `#` in a CSV are treated as notes and ignored. `backup/faq.csv` uses one to mark the FAQ as a draft for ISD to review.

### Sheet tabs and columns

| Tab | Columns | Notes |
|---|---|---|
| Dogs | name, breed, age, bio, training_stage, photo_file, alt_text, instagram_url, sponsor_link, status | stage is 1 to 4 (names in `config.TRAINING_STAGES`); status is in_training, placed or retired |
| FAQ | question, answer, category, keywords | category is one of the keys of `content.FAQ_CATEGORIES` (applying, service_dogs, etiquette, donating, sponsoring, puppy_raising, volunteering, about_isd, general); `etiquette` rows also fill the Respect the Vest page |
| Events | title, date, start_time, location, description, link | date is YYYY-MM-DD (M/D/YYYY also works); past events hide themselves |
| SponsorTiers | tier_name, amount, covers, payment_link, sort_order | ISD's giving levels ($1 to $10,000); a level whose amount is a placeholder is hidden |
| SiteText | key, value, where_it_shows | `where_it_shows` is only a note for editors; the keys the app reads are in `content.SITE_TEXT_KEYS`. `stat_1`..`stat_4` use `number|label` |
| News | title, date, body, photo_file, alt_text | newest first; a blank line inside `body` starts a new paragraph |
| Team | name, role, board, photo_file, alt_text, sort_order | board is administrative, executive or advisory; no photo shows initials |
| Sponsors | name, link, logo_file, alt_text, sort_order | no logo shows the name as text |
| Gallery | photo_file, alt_text, caption, sort_order | the photo grid on Meet the Dogs |
| Roles | title, description, details_link, is_open | open volunteer roles on Get Involved; `is_open` = no hides one |

## Refreshing the backup

The backup is what visitors see if Google is unreachable, so keep it reasonably fresh (every few months, or after big edits):

```bash
python scripts/refresh_backup.py
git add backup && git commit -m "Refresh content backup"
```

The script uses the same links as the site (`.streamlit/secrets.toml` if present, otherwise `config.py`) and only overwrites a tab that downloads cleanly with the right columns.

## The chatbot

`chatbot.FaqMatcher` blends two TF-IDF similarities against each FAQ row:

- **Word match (70%):** word unigrams and bigrams after stop-word removal and a small suffix stemmer, over the question and keywords (weighted 3x) plus the answer.
- **Fuzzy match (30%):** 3–5 letter chunks of the question and keywords, so typos like "sponser" or "aply" still land nearby (`config.CHATBOT_FUZZY_WEIGHT`).

What the visitor gets depends on the best score:

| Score | Reply |
|---|---|
| ≥ `CHATBOT_THRESHOLD` (0.25) | The answer, a link to the matching page (by FAQ category, `chat_ui.MORE`), and up to 3 related questions |
| ≥ `CHATBOT_SUGGEST_THRESHOLD` (0.12) | "Did you mean…?" buttons for the closest questions, plus the contact email |
| lower | The contact email |

Greetings, thanks, goodbyes and "are you a bot?" get short replies from SiteText (`chatbot_greeting`, `chatbot_thanks`, `chatbot_bye`, `chatbot_about`) instead of a failed match.

Tuning lives in `tests/test_chatbot.py`: 31 real questions (lowest score 0.27), 6 misspelled ones (answered or suggested correctly), and 6 off-topic ones (0.19 or lower). The usual fix for a missed question is adding phrases to that row's `keywords` cell, not changing code. Known limit: an off-topic question that happens to share words with an FAQ (e.g. "where can I buy a used car") can still get an answer.

`chat_ui.py` draws the chat. The Ask ISD page and the pop-up pinned bottom-right on every other page share one conversation; nothing typed is saved.

A paid LLM is deliberately not wired in. If ISD ever wants one, add it as an optional rephrasing step that only runs when a key exists in secrets and only rephrases the matched FAQ answer.

## Tests

```bash
pytest
```

- `test_content.py`: backup loads, bad or unreachable links fall back, missing columns don't crash, past events hide, empty and bad rows are handled.
- `test_chatbot.py`: 31 realistic questions reach the right FAQ entry, 6 misspelled ones are answered or suggested correctly, 6 off-topic ones fall below the threshold, plus small-talk detection.
- `test_pages.py`: every page renders without errors (via `streamlit.testing.AppTest`) with the backup content and with a filled-in copy, has exactly one h1, and has alt text on every image; plus checks that ISD's real content (graduates, leadership, sponsors, news) shows up.

Tests never touch the live Sheet: `tests/conftest.py` blanks the links so everything runs from `backup/` or a temp copy.

## Deploy (Streamlit Community Cloud, free)

1. Push this folder to a GitHub repo **owned by an ISD account** (for example the tech_support@ Google/GitHub login), not a student's personal account.
2. At https://share.streamlit.io, sign in with that GitHub account and choose **Create app**. Pick the repo, branch `main`, main file `app.py`, and Python 3.11 or newer.
3. No secrets are required, because the Sheet links are in `config.py`. To override them, paste a `[sheets]` block (see `secrets.toml.example`) under **Advanced settings → Secrets**.
4. Deploy. Every push to `main` redeploys automatically.

To switch Sheets later without a code change, add the new links in **App → Settings → Secrets**.

**Handing over ownership:** transfer the repo on GitHub (**Settings → Transfer ownership**) to the ISD account. Then have ISD sign in to share.streamlit.io with that account and redeploy from the transferred repo. Use the same app URL after deleting the old app, or a new one. Finally, remove the student accounts.

Free apps go to sleep after a stretch with no visitors and take a few seconds to wake up. Linking the site from illiniservicedogs.com keeps it busier.

## The Google Sheet

ISD's content lives in [ISD Website Content](https://docs.google.com/spreadsheets/d/1ivz6uGEAkoSfOUGJb7VPgHiHCoCm7T0-rO1-WGnRxgo/edit). It has a "Start here" tab for editors, plus the ten tabs the site reads.

**How the site reads it:** the Sheet is shared as **Anyone with the link: Viewer**, and each tab is downloaded as CSV from

```
https://docs.google.com/spreadsheets/d/<SHEET_ID>/export?format=csv&gid=<TAB_GID>
```

These links are in `config.SHEET_URLS`. Edits show up on the site as soon as the 10-minute cache expires, with no publish step. Anyone with the link can view the Sheet, which is fine because everything in it is already public on the website. **Never put private information in this Sheet.**

**If you ever rebuild the Sheet:**
1. Create a Google Sheet with tabs named exactly `Dogs`, `FAQ`, `Events`, `SponsorTiers`, `SiteText`. For each one, use **File → Import → Upload** with the matching file from `backup/` and choose **Replace current sheet**.
2. Click **Share → General access → Anyone with the link → Viewer**.
3. Open each tab and copy the `gid=` number from the address bar. Put the five links in `config.SHEET_URLS`, or in Streamlit secrets to change them without a code change.
4. Open the Content Check page. All five tabs should say "loaded live".

**Ownership:** the Sheet was created in Ved Kulkarni's Google Drive. At handoff, use **Share → (ISD account) → Transfer ownership** to move it to ISD's Google account. The file ID and links stay the same, so nothing on the site needs to change.
