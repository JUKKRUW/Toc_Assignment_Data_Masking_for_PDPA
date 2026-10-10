"""API contract tests (owner: M08). The shapes here are what the frontend relies on."""
import io

import pytest

from pdpa_shield.app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.testing = True
    return app.test_client()


def test_health(client):
    assert client.get("/api/health").get_json()["rules"] == ["card", "email", "phone", "dob", "address"]


def test_mask_shape(client):
    data = client.post("/api/mask", json={"text": "hello"}).get_json()
    assert set(data) == {"parts", "masked", "stats"}
    assert data["masked"] == "hello"
    assert set(data["stats"]) == {"counts", "total", "risk", "level", "level_code"}


def test_upload_thai_encodings(client):
    for enc in ("utf-8", "cp874"):
        raw = "Address: 689 ถนนลาดกระบัง".encode(enc)
        data = client.post("/api/upload", data={"file": (io.BytesIO(raw), "a.log")},
                           content_type="multipart/form-data").get_json()
        assert data["text"].startswith("Address: 689 ถนน")


def test_upload_missing_file(client):
    assert client.post("/api/upload", data={}, content_type="multipart/form-data").status_code == 400


def test_generate_clamps(client):
    text = client.get("/api/generate?n=1").get_json()["text"]
    assert len(text.splitlines()) == 5


def test_rules_shape(client):
    rules = client.get("/api/rules").get_json()
    assert [r["key"] for r in rules] == ["card", "email", "phone", "dob", "address"]
    need = {"key", "label", "label_en", "color", "weight", "pattern", "flags", "target",
            "explain", "explain_en", "example", "example_masked", "tokens"}
    assert need <= set(rules[0])


def test_tests_shape(client):
    rows = client.get("/api/tests").get_json()
    need = {"category", "name_th", "name_en", "negative", "input", "expected", "actual", "passed"}
    assert need <= set(rows[0])
