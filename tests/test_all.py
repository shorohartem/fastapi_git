import pytest
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
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_json():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()



def test_app_title():
    assert app.title == "OCR Service"


def test_app_docs_url():
    assert app.docs_url == "/docs"
