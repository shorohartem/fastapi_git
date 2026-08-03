from io import BytesIO
from unittest.mock import Mock

from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import settings
from app.main import app

client = TestClient(app)


def make_png() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (20, 20), color="white").save(buffer, format="PNG")
    return buffer.getvalue()


def upload_test_photo(tmp_path, monkeypatch) -> dict:
    monkeypatch.setattr(settings, "MEDIA_ROOT", str(tmp_path))
    response = client.post(
        "/api/v1/photos",
        files={"file": ("document.png", make_png(), "image/png")},
    )
    assert response.status_code == 201
    return response.json()


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "True"}


def test_health_method_not_allowed():
    response = client.post("/health")
    assert response.status_code == 405


def test_docs_available():
    assert client.get("/").status_code == 200


def test_openapi_json():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()


def test_app_configuration():
    assert app.title == "OCR Service"
    assert app.docs_url == "/"


def test_upload_photo_returns_persistent_id(tmp_path, monkeypatch):
    photo = upload_test_photo(tmp_path, monkeypatch)

    assert photo["id"] == 1
    assert photo["original_filename"] == "document.png"
    assert photo["content_type"] == "image/png"
    assert (tmp_path / "photos.sqlite3").is_file()
    assert len(list((tmp_path / "uploads").glob("*.png"))) == 1


def test_analyze_doc_returns_text_by_id(tmp_path, monkeypatch):
    photo = upload_test_photo(tmp_path, monkeypatch)
    extract_text = Mock(return_value="Recognized text")
    monkeypatch.setattr(
        "app.api.router.TesseractOCRService.extract_text",
        extract_text,
    )

    response = client.post(f"/api/v1/analyze_doc?photo_id={photo['id']}")

    assert response.status_code == 200
    assert response.json() == {"photo_id": photo["id"], "text": "Recognized text"}
    stored_path = extract_text.call_args.args[0]
    assert stored_path.startswith("uploads/")
    assert (tmp_path / stored_path).is_file()


def test_analyze_unknown_photo_returns_404(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "MEDIA_ROOT", str(tmp_path))

    response = client.post("/api/v1/analyze_doc?photo_id=999")

    assert response.status_code == 404


def test_send_message_to_email_uses_photo_id(tmp_path, monkeypatch):
    photo = upload_test_photo(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "app.api.router.TesseractOCRService.extract_text",
        Mock(return_value="Text for email"),
    )
    send_notification = Mock(return_value=True)
    monkeypatch.setattr(
        "app.api.router.SMTPEmailService.send_notification",
        send_notification,
    )

    response = client.post(
        "/api/v1/send_message_to_email",
        json={
            "photo_id": photo["id"],
            "recipient_email": "student@example.com",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "photo_id": photo["id"],
        "recipient_email": "student@example.com",
        "email_sent": True,
    }
    send_notification.assert_called_once()
