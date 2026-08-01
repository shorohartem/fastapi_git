import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_method_not_allowed():
    response = client.post("/health")
    assert response.status_code == 405


def test_docs_available():
    response = client.get("/")
    assert response.status_code == 200


def test_openapi_json():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()



def test_app_title():
    assert app.title == "OCR Service"


def test_app_docs_url():
    assert app.docs_url == "/"


def test_analyze_doc_queues_celery_task(monkeypatch):
    queued_task = Mock(id="ocr-task-id")
    monkeypatch.setattr(
        "app.api.router.analyze_document.delay",
        Mock(return_value=queued_task),
    )

    response = client.post(
        "/api/v1/analyze_doc",
        json={"image_path": "photo.jpg"},
    )

    assert response.status_code == 202
    assert response.json() == {"task_id": "ocr-task-id", "status": "queued"}


def test_send_email_queues_celery_task(monkeypatch):
    delay = Mock(return_value=Mock(id="email-task-id"))
    monkeypatch.setattr("app.api.router.send_email_notification.delay", delay)

    response = client.post(
        "/api/v1/send_message_to_email",
        json={
            "image_path": "photo.jpg",
            "extracted_text": "Recognized text",
            "recipient_email": "student@example.com",
        },
    )

    assert response.status_code == 202
    assert response.json() == {"task_id": "email-task-id", "status": "queued"}
    delay.assert_called_once_with(
        "student@example.com",
        "photo.jpg",
        "Recognized text",
    )
