"""Tests for FastAPI application."""
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_should_create_fastapi_app_instance():
    """Test that app is a FastAPI instance with correct title."""
    from benz_news_context.app import app

    assert isinstance(app, FastAPI)
    assert app.title == "benz_news_context"


def test_health_endpoint_returns_200():
    """Test that health endpoint returns 200 with correct status."""
    from benz_news_context.app import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_app_has_openapi_schema():
    """Test that app generates valid OpenAPI schema."""
    from benz_news_context.app import app

    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "benz_news_context"
