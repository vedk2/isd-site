import pytest

import content


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """Tests never touch the live Google Sheet; they use backup/ (or a temp copy)."""
    monkeypatch.setattr(content, "sheet_url", lambda key: "")
