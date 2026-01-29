"""Tests for FastAPI application."""
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_should_create_fastapi_app_instance():
    """Test that app is a FastAPI instance with correct title."""
    from benz_news_context.app import app

    assert isinstance(app, FastAPI)
    assert app.title == "benz_news_context"


def test_health_endpoint_returns_200(mock_database_adapter):
    """Test that health endpoint returns 200 with correct status."""
    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    # Override dependency with mock
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    # With database integration, health check includes database status
    assert response.json() == {"status": "healthy", "database": "connected"}

    # Clean up
    app.dependency_overrides.clear()


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


def test_health_endpoint_checks_database_connection(mock_database_adapter):
    """Test that health endpoint validates database connection."""
    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    # Override dependency with mock
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}

    # Verify database was queried
    cursor = (
        mock_database_adapter.read_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    )
    cursor.execute.assert_called_once()

    # Clean up
    app.dependency_overrides.clear()


def test_health_endpoint_handles_database_error(mock_database_adapter):
    """Test that health endpoint returns 503 on database error."""
    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    # Configure mock to raise exception
    mock_database_adapter.read_connection.side_effect = Exception("Database connection failed")

    # Override dependency with mock
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 503
    response_data = response.json()
    assert "detail" in response_data
    detail = response_data["detail"]
    assert detail["status"] == "unhealthy"
    assert detail["database"] == "error"
    assert "error" in detail

    # Clean up
    app.dependency_overrides.clear()
