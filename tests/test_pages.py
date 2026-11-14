"""Render every page with Streamlit's test runner and fail on any error.

Runs twice: once with the real backup/ files (lots of [ISD to confirm]) and once
with a fully filled-in copy, so both the "coming soon" and the finished states work.
"""

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


@pytest.mark.parametrize("path", PAGES)
def test_page_renders_with_seed_content(path):
    at = run_page(path)
    assert not at.exception, at.exception
    assert len(at.title) == 1  # exactly one h1 per page


@pytest.fixture
def filled(tmp_path, monkeypatch):
    backup = tmp_path / "backup"
    shutil.copytree(config.BACKUP_DIR, backup)
    images = tmp_path / "images"
    images.mkdir()
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


def test_filled_home_shows_next_event_and_dogs(filled):
    at = run_page(ui.PAGES["home"])
    headers = [h.value for h in at.header]
    assert "Next event" in headers and "Dogs in training" in headers


def test_chatbot_answers_and_falls_back():
    at = run_page(ui.PAGES["ask"])
    at.chat_input[0].set_value("how much does a dog cost").run()
    assert any("free of charge" in m.value for m in at.markdown)
    at.chat_input[0].set_value("best pizza near campus").run()
    assert any("ContactUs@illiniservicedogs.com" in m.value for m in at.markdown)
