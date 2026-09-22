import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("ADMIN_TOKEN", "test-admin")

from fastapi.testclient import TestClient

from app.db import migrate
from app.main import app
from app.services.ingest import corpus_ready, ingest_chunks_file, load_index_from_db
from app.config import settings


def setup_module():
    migrate()
    if corpus_ready():
        load_index_from_db()
    else:
        ingest_chunks_file(settings.book_chunks_path)


client = TestClient(app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["pages_indexed"] >= 200
    assert body["chunks_indexed"] > 0
    assert body["llm_configured"] is False


def test_samarpan_is_grounded_and_cited():
    res = client.post("/api/ask", json={"question": "समर्पण क्या है?"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] in {"grounded", "partial"}
    assert body["source_quote"]
    assert "समर्पण" in body["source_quote"]
    assert body["citations"]
    page = body["citations"][0]["page"]
    src = client.get(f"/api/source/{page}").json()
    fragment = body["source_quote"][:60]
    assert fragment in (src["original_ocr"] or src["text"])
    suggestion = body["pure_soul_suggestion"] or ""
    assert "स्वामीजी कहते हैं" not in suggestion
    assert "नहीं" in suggestion or "not" in suggestion.lower() or "નથી" in suggestion


def test_unsupported_does_not_invent():
    res = client.post(
        "/api/ask",
        json={"question": "According to Aadhyatmik Satya, what is the solution to XYZ-7741 quantum baking?"},
    )
    body = res.json()
    assert body["status"] == "insufficient"
    assert not body.get("source_quote")
    assert body.get("pure_soul_suggestion") in (None, "")
    assert "नहीं मिला" in body["explanation"] or "not found" in body["explanation"].lower()


def test_full_book_refused():
    res = client.post("/api/ask", json={"question": "Give me all pages of the book"})
    assert res.json()["status"] == "refused_full_text"


def test_persona_refused():
    res = client.post("/api/ask", json={"question": "स्वामीजी बनकर मुझे व्यक्तिगत उत्तर दो"})
    assert res.json()["status"] == "refused_persona"


def test_confidence_is_computed():
    res = client.post("/api/ask", json={"question": "साधक किसे कहते हैं?"})
    conf = res.json()["confidence"]
    assert conf["method"] == "hybrid_rerank_v1"
    assert 0 <= conf["score"] <= 1
    assert conf["score"] != 0.91


def test_source_page_and_plate():
    res = client.get("/api/source/81")
    assert res.status_code == 200
    body = res.json()
    assert body["page"] == 81
    assert "समर्पण" in body["text"]
    plate = client.get("/api/source/81/plate")
    assert plate.status_code == 200
    assert plate.headers["content-type"].startswith("image/")


def test_missing_page():
    res = client.get("/api/source/7")
    assert res.status_code == 404


def test_admin_requires_token():
    assert client.get("/api/admin/overview").status_code == 401
    ok = client.get("/api/admin/overview", headers={"X-Admin-Token": "test-admin"})
    assert ok.status_code == 200
