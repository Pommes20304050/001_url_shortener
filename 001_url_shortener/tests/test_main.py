"""Tests for URL Shortener."""
import pytest
import os
import sys

# Testdatenbank in temp-Verzeichnis
os.environ.setdefault("TESTING", "1")

from src.models import generate_code, is_valid_url, ShortURL


# ── models ─────────────────────────────────────────────────────────────────

def test_generate_code_length():
    assert len(generate_code()) == 6

def test_generate_code_custom_length():
    assert len(generate_code(8)) == 8

def test_generate_code_unique():
    codes = {generate_code() for _ in range(100)}
    assert len(codes) > 90  # soll fast immer unique sein

def test_is_valid_url_http():
    assert is_valid_url("http://example.com") is True

def test_is_valid_url_https():
    assert is_valid_url("https://google.com/search?q=test") is True

def test_is_valid_url_no_scheme():
    assert is_valid_url("example.com") is False

def test_is_valid_url_ftp():
    assert is_valid_url("ftp://example.com") is False

def test_is_valid_url_empty():
    assert is_valid_url("") is False

def test_short_url_display_code_alias():
    su = ShortURL(code="abc123", long_url="https://x.com", alias="mein",
                  clicks=0, created_at="2024-01-01", last_click=None)
    assert su.display_code == "mein"

def test_short_url_display_code_no_alias():
    su = ShortURL(code="abc123", long_url="https://x.com", alias=None,
                  clicks=0, created_at="2024-01-01", last_click=None)
    assert su.display_code == "abc123"

def test_short_url_short_link():
    su = ShortURL(code="abc123", long_url="https://x.com", alias=None,
                  clicks=0, created_at="2024-01-01", last_click=None)
    assert su.short_link("http://localhost:5000") == "http://localhost:5000/abc123"


# ── Flask API ──────────────────────────────────────────────────────────────

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("src.db.DB_PATH", str(tmp_path / "test.db"))
    from src import db as _db
    _db.init_db()
    from src.app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_index_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200

def test_shorten_api(client):
    resp = client.post("/api/shorten",
                       json={"url": "https://example.com"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "short_url" in data
    assert data["long_url"] == "https://example.com"

def test_shorten_invalid_url(client):
    resp = client.post("/api/shorten", json={"url": "not-a-url"})
    assert resp.status_code == 400

def test_shorten_with_alias(client):
    resp = client.post("/api/shorten",
                       json={"url": "https://example.com", "alias": "test"})
    assert resp.status_code == 200
    assert resp.get_json()["code"] == "test"

def test_redirect(client):
    client.post("/api/shorten", json={"url": "https://example.com", "alias": "go"})
    resp = client.get("/go")
    assert resp.status_code == 302
    assert "example.com" in resp.headers["Location"]

def test_redirect_not_found(client):
    resp = client.get("/gibtsNicht")
    assert resp.status_code == 404

def test_duplicate_alias(client):
    client.post("/api/shorten", json={"url": "https://a.com", "alias": "doppelt"})
    resp = client.post("/api/shorten", json={"url": "https://b.com", "alias": "doppelt"})
    assert resp.status_code == 409

def test_stats_api(client):
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total_urls" in data
    assert "total_clicks" in data
