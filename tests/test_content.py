from datetime import date
from pathlib import Path

import pytest

import config
import content
from content import TABS, load_tab_uncached, parse_date, upcoming_events

BACKUP = config.BACKUP_DIR


@pytest.mark.parametrize("key", list(TABS))
def test_every_backup_tab_loads(key):
    result = load_tab_uncached(key, url="")
    assert result.source == "backup"
    assert not result.rows.empty
    assert list(result.rows.columns) == list(TABS[key].columns)


def test_backup_seed_content():
    dogs = load_tab_uncached("dogs", "").rows
    assert set(dogs[dogs["status"] == "in_training"]["name"]) == {"Millie", "Morrie", "Rory", "Cairo", "Bear"}
    assert set(dogs[dogs["status"] == "placed"]["name"]) == {"Ike", "Alma", "Maizey", "Abe"}
    faq = load_tab_uncached("faq", "").rows
    assert len(faq) >= 25
    text = {r["key"]: r["value"] for r in load_tab_uncached("site_text", "").rows.to_dict("records")}
    for key in content.SITE_TEXT_KEYS:
        assert key in text, key


def test_bad_url_falls_back_to_backup():
    result = load_tab_uncached("faq", "https://127.0.0.1:9/nothing.csv", timeout=1)
    assert result.source == "backup"
    assert not result.rows.empty
    assert any("Couldn't reach" in n for n in result.notes)


def test_non_web_link_falls_back(tmp_path):
    result = load_tab_uncached("faq", "not a link at all")
    assert result.source == "backup"


def test_live_sheet_is_used_when_it_works(monkeypatch):
    csv = "question,answer,category,keywords\nIs it free?,Yes it is.,applying,cost\n"
    monkeypatch.setattr(content, "_fetch_text", lambda url, timeout: csv)
    result = load_tab_uncached("faq", "https://example.com/faq.csv")
    assert result.source == "live"
    assert result.rows.iloc[0]["answer"] == "Yes it is."


def test_live_sheet_missing_required_column_uses_backup(monkeypatch):
    monkeypatch.setattr(content, "_fetch_text", lambda url, timeout: "question,category\nHi?,general\n")
    result = load_tab_uncached("faq", "https://example.com/faq.csv")
    assert result.source == "backup"
    assert any("missing the column" in n for n in result.notes)


def test_missing_optional_column_does_not_crash(tmp_path):
    (tmp_path / "dogs.csv").write_text("name,status\nMillie,in_training\n")
    result = load_tab_uncached("dogs", "", backup_dir=tmp_path)
    assert result.rows.iloc[0]["name"] == "Millie"
    assert result.rows.iloc[0]["breed"] == ""
    assert result.rows.iloc[0]["training_stage"] is None


def test_missing_backup_file_does_not_crash(tmp_path):
    result = load_tab_uncached("events", "", backup_dir=tmp_path)
    assert result.source == "missing"
    assert result.rows.empty


def test_empty_rows_dropped_and_bad_rows_skipped(tmp_path):
    (tmp_path / "dogs.csv").write_text(
        "name,breed,status,training_stage\n"
        "  Millie  , Lab ,in_training,2\n"
        ",,,\n"
        "\n"
        ",Lab,in_training,1\n"
        "Rex,Lab,on vacation,1\n"
        "Bear,Lab,Placed,seven\n"
    )
    result = load_tab_uncached("dogs", "", backup_dir=tmp_path)
    rows = result.rows.to_dict("records")
    assert [r["name"] for r in rows] == ["Millie", "Bear"]
    assert rows[0]["breed"] == "Lab"            # whitespace stripped
    assert rows[0]["training_stage"] == 2       # type coerced
    assert rows[1]["status"] == "placed"        # normalized
    assert rows[1]["training_stage"] is None    # bad number kept as "unknown", row not lost
    assert len(result.skipped) == 2             # no name, bad status


def test_faq_empty_answer_is_skipped(tmp_path):
    (tmp_path / "faq.csv").write_text("question,answer,category\nA?,Yes,donating\nB?,,general\nC?,Sure,Weird\n")
    result = load_tab_uncached("faq", "", backup_dir=tmp_path)
    assert list(result.rows["question"]) == ["A?", "C?"]
    assert result.rows.iloc[1]["category"] == "general"
    assert "empty answer" in result.skipped[0]


def test_comment_lines_at_top_are_ignored(tmp_path):
    (tmp_path / "faq.csv").write_text("# Draft, ISD to review.\nquestion,answer\nA?,Yes\n")
    assert len(load_tab_uncached("faq", "", backup_dir=tmp_path).rows) == 1


@pytest.mark.parametrize("text,expected", [
    ("2027-03-14", date(2027, 3, 14)),
    ("3/14/2027", date(2027, 3, 14)),
    ("March 14, 2027", date(2027, 3, 14)),
    ("next tuesday", None),
    ("", None),
])
def test_parse_date(text, expected):
    assert parse_date(text) == expected


def test_past_events_are_hidden_and_sorted(tmp_path):
    (tmp_path / "events.csv").write_text(
        "title,date\nLater,2027-05-01\nOld,2026-01-01\nToday,2026-11-14\nSoon,11/20/2026\nBroken,someday\n"
    )
    result = load_tab_uncached("events", "", backup_dir=tmp_path)
    upcoming = upcoming_events(result.rows, today=date(2026, 11, 14))
    assert list(upcoming["title"]) == ["Today", "Soon", "Later"]
    assert any("Broken" in s for s in result.skipped)


def test_sponsor_tier_sort_order_coerced(tmp_path):
    (tmp_path / "sponsor_tiers.csv").write_text("tier_name,amount,sort_order\nB,$50,2\nA,$25,1\nC,$5,\n")
    rows = load_tab_uncached("sponsor_tiers", "", backup_dir=tmp_path).rows
    assert list(rows.sort_values("sort_order")["tier_name"]) == ["A", "B", "C"]


def test_placeholders_and_urls():
    assert content.is_placeholder("[ISD to confirm]")
    assert content.is_placeholder("$XX")
    assert content.is_placeholder("  ")
    assert not content.is_placeholder("$25")
    assert content.safe_url("https://a.co/d0Be1a6") == "https://a.co/d0Be1a6"
    assert content.safe_url("[ISD to confirm]") == ""
    assert content.safe_url("javascript:alert(1)") == ""


def test_photo_path_cannot_escape_images_folder():
    assert content.photo_path("../config.py") is None
    assert content.photo_path("missing.jpg") is None
