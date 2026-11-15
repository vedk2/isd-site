"""Render every page with Streamlit's test runner and fail on any error.

Runs twice: once with the real backup/ files (lots of [ISD to confirm]) and once
with a fully filled-in copy, so both the "coming soon" and the finished states work.
"""

import re
import shutil
from datetime import date, timedelta

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

import config
import ui

PAGES = list(ui.PAGES.values())


def run_page(path):
    at = AppTest.from_file("../app.py", default_timeout=30)
    at.run()
    if path != ui.PAGES["home"]:
        at.switch_page(path)
        at.run()
    return at


@pytest.fixture(autouse=True)
def fresh_cache():
    st.cache_data.clear()
    st.cache_resource.clear()
    yield
    st.cache_data.clear()
    st.cache_resource.clear()


def page_html(at) -> str:
    return "".join(h.proto.body for h in at.get("html"))


def assert_accessible(at):
    markup = page_html(at)
    assert markup.count("<h1") + len(at.title) == 1, "every page needs exactly one h1"
    for img in re.findall(r"<img[^>]*>", markup):
        assert re.search(r'alt="[^"]+"', img), f"image without alt text: {img[:120]}"


@pytest.mark.parametrize("path", PAGES)
def test_page_renders_with_seed_content(path):
    at = run_page(path)
    assert not at.exception, at.exception
    assert_accessible(at)


@pytest.fixture
def filled(tmp_path, monkeypatch):
    backup = tmp_path / "backup"
    shutil.copytree(config.BACKUP_DIR, backup)
    images = tmp_path / "images"
    shutil.copytree(config.IMAGES_DIR, images)
    # A tiny valid PNG for Millie.
    (images / "millie.jpg").write_bytes(bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
        "1f15c4890000000d49444154789c6360f8ffff3f0005fe02fea7d6a4"
        "c70000000049454e44ae426082"))
    soon = (date.today() + timedelta(days=7)).isoformat()
    (backup / "dogs.csv").write_text(
        "name,breed,age,bio,training_stage,photo_file,alt_text,instagram_url,sponsor_link,status\n"
        "Millie,Labrador,2,Loves fetch.,2,millie.jpg,Yellow lab sitting on grass,https://instagram.com/x,,in_training\n"
        "Morrie,Golden,1,Calm.,4,,,,https://paypal.me/x,in_training\n"
        "Coal,Lab,10,The first ISD dog.,,,,,,placed\n")
    (backup / "events.csv").write_text(
        f"title,date,start_time,location,description,link\n"
        f"Pet-A-Pup,{soon},2 PM,Main Quad,Meet the dogs for $5 or $10.,https://example.com\n")
    (backup / "sponsor_tiers.csv").write_text(
        "tier_name,amount,covers,payment_link,sort_order\n"
        "Food,$25,A month of food,https://paypal.me/x,1\nVet,$100,A vet visit,,2\n")
    text = (backup / "site_text.csv").read_text().replace("[ISD to confirm]", "https://example.com")
    (backup / "site_text.csv").write_text(text + "newsletter_url,https://example.com/news,\n")
    monkeypatch.setattr(config, "BACKUP_DIR", backup)
    monkeypatch.setattr(config, "IMAGES_DIR", images)


@pytest.mark.parametrize("path", PAGES)
def test_page_renders_with_filled_content(filled, path):
    at = run_page(path)
    assert not at.exception, at.exception
    assert_accessible(at)


def test_filled_home_shows_events_dogs_and_news(filled):
    markup = page_html(run_page(ui.PAGES["home"]))
    for text in ("Upcoming events", "Meet the dogs in training", "Program news", "Pet-A-Pup", "Millie"):
        assert text in markup, text


def test_seed_pages_show_real_isd_content():
    assert "Maizey" in page_html(run_page(ui.PAGES["dogs"]))
    about = page_html(run_page(ui.PAGES["about"]))
    assert "Mary Guth" in about and "Hinsdale Humane Society" in about
    assert "Welcome, Lincoln!" in page_html(run_page(ui.PAGES["news"]))


def test_chatbot_answers_and_falls_back():
    at = run_page(ui.PAGES["ask"])
    at.chat_input[0].set_value("is there a fee to get a service dog").run()
    assert any("no cost" in m.value for m in at.markdown)
    at.chat_input[0].set_value("best pizza near campus").run()
    assert any("ContactUs@illiniservicedogs.com" in m.value for m in at.markdown)


def test_floating_chat_on_other_pages_answers_questions():
    at = run_page(ui.PAGES["dogs"])
    assert len(at.chat_input) == 1, "the pop-up chat should be on every page except Ask ISD"
    at.chat_input[0].set_value("is there a fee to get a service dog").run()
    assert not at.exception
    assert any("no cost" in m.value for m in at.markdown)


def test_ask_page_has_only_the_full_chat():
    at = run_page(ui.PAGES["ask"])
    assert len(at.chat_input) == 1


def test_chat_small_talk_suggestions_and_page_links():
    at = run_page(ui.PAGES["ask"])
    at.chat_input[0].set_value("hello").run()
    assert any("What would you like to know" in m.value for m in at.markdown)
    at.chat_input[0].set_value("can i sponser a dog").run()
    assert any("Did you mean" in m.value for m in at.markdown)
    assert any(b.label == "How do I sponsor a dog?" for b in at.button)
    at.chat_input[0].set_value("how long is the waitlist").run()
    assert not at.exception
