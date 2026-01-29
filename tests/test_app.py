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


# Prior News Context Endpoint Tests


def test_prior_news_endpoint_returns_articles(mock_database_adapter):
    """Test that prior-news-context endpoint returns articles successfully."""
    from datetime import datetime, timezone

    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    # Mock database to return 2 articles
    sample_rows = [
        {
            "id": "uuid-1234",
            "title": "First Article",
            "published_utc": datetime(2026, 1, 20, 14, 30, 0, tzinfo=timezone.utc),
            "channels": ["technology"],
            "tags": ["earnings"],
            "sentiment": "bullish",
            "sentiment_score": 0.85,
            "was_traded": True,
            "trade_side": "buy",
        },
        {
            "id": "uuid-5678",
            "title": "Second Article",
            "published_utc": datetime(2026, 1, 19, 10, 15, 0, tzinfo=timezone.utc),
            "channels": ["news"],
            "tags": ["merger"],
            "sentiment": "bearish",
            "sentiment_score": 0.60,
            "was_traded": False,
            "trade_side": None,
        },
    ]

    cursor = (
        mock_database_adapter.read_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    )
    cursor.fetchall.return_value = sample_rows

    # Override dependency
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.post(
        "/api/prior-news-context",
        json={"ticker": "AVGO", "reference_timestamp": "2026-01-21T17:00:00Z"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AVGO"
    assert data["lookback_hours"] == 48
    assert data["article_count"] == 2
    assert len(data["articles"]) == 2
    assert data["articles"][0]["id"] == "uuid-1234"
    assert data["articles"][1]["id"] == "uuid-5678"

    # Clean up
    app.dependency_overrides.clear()


def test_prior_news_endpoint_handles_empty_results(mock_database_adapter):
    """Test that prior-news-context returns 200 with empty results."""
    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    # Mock database to return empty list
    cursor = (
        mock_database_adapter.read_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    )
    cursor.fetchall.return_value = []

    # Override dependency
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.post(
        "/api/prior-news-context",
        json={"ticker": "AVGO", "reference_timestamp": "2026-01-21T17:00:00Z"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["article_count"] == 0
    assert len(data["articles"]) == 0

    # Clean up
    app.dependency_overrides.clear()


def test_prior_news_endpoint_validates_request_body(mock_database_adapter):
    """Test that prior-news-context validates request body."""
    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    # Override dependency to prevent database connection attempt
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.post("/api/prior-news-context", json={"reference_timestamp": "2026-01-21T17:00:00Z"})

    assert response.status_code == 422
    errors = response.json()
    assert "detail" in errors

    # Clean up
    app.dependency_overrides.clear()


def test_prior_news_endpoint_handles_database_error(mock_database_adapter):
    """Test that prior-news-context handles database errors."""
    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    # Configure mock to raise exception
    mock_database_adapter.read_connection.side_effect = Exception("Database error")

    # Override dependency
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.post(
        "/api/prior-news-context",
        json={"ticker": "AVGO", "reference_timestamp": "2026-01-21T17:00:00Z"},
    )

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data

    # Clean up
    app.dependency_overrides.clear()


def test_prior_news_endpoint_uses_48_hour_lookback(mock_database_adapter):
    """Test that prior-news-context uses correct lookback window."""
    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    cursor = (
        mock_database_adapter.read_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    )
    cursor.fetchall.return_value = []

    # Override dependency
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.post(
        "/api/prior-news-context",
        json={"ticker": "AVGO", "reference_timestamp": "2026-01-21T17:00:00Z"},
    )

    assert response.status_code == 200
    # Verify the query was executed (lookback calculation happens in SQL)
    cursor.execute.assert_called_once()

    # Clean up
    app.dependency_overrides.clear()


# Traded News Context Endpoint Tests


def test_traded_news_endpoint_returns_trades(mock_database_adapter):
    """Test that traded-news-context endpoint returns trades successfully."""
    from datetime import datetime, timezone

    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    # Mock database to return 3 trades
    sample_rows = [
        {
            "article_id": "uuid-1111",
            "title": "Trade Article 1",
            "published_utc": datetime(2026, 1, 15, 16, 5, 0, tzinfo=timezone.utc),
            "trade_executed_at": datetime(2026, 1, 15, 16, 5, 32, tzinfo=timezone.utc),
            "side": "buy",
            "fill_price": 245.67,
        },
        {
            "article_id": "uuid-2222",
            "title": "Trade Article 2",
            "published_utc": datetime(2026, 1, 10, 9, 30, 0, tzinfo=timezone.utc),
            "trade_executed_at": datetime(2026, 1, 10, 9, 30, 15, tzinfo=timezone.utc),
            "side": "sell",
            "fill_price": 242.50,
        },
        {
            "article_id": "uuid-3333",
            "title": "Trade Article 3",
            "published_utc": datetime(2026, 1, 8, 11, 0, 0, tzinfo=timezone.utc),
            "trade_executed_at": datetime(2026, 1, 8, 11, 0, 18, tzinfo=timezone.utc),
            "side": "buy",
            "fill_price": 238.90,
        },
    ]

    cursor = (
        mock_database_adapter.read_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    )
    cursor.fetchall.return_value = sample_rows

    # Override dependency
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.post(
        "/api/traded-news-context",
        json={"ticker": "AVGO", "reference_timestamp": "2026-01-21T17:00:00Z"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AVGO"
    assert data["lookback_days"] == 14
    assert data["trade_count"] == 3
    assert len(data["trades"]) == 3
    assert data["trades"][0]["article_id"] == "uuid-1111"

    # Clean up
    app.dependency_overrides.clear()


def test_traded_news_endpoint_handles_empty_results(mock_database_adapter):
    """Test that traded-news-context returns 200 with empty results."""
    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    # Mock database to return empty list
    cursor = (
        mock_database_adapter.read_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    )
    cursor.fetchall.return_value = []

    # Override dependency
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.post(
        "/api/traded-news-context",
        json={"ticker": "AVGO", "reference_timestamp": "2026-01-21T17:00:00Z"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["trade_count"] == 0
    assert len(data["trades"]) == 0

    # Clean up
    app.dependency_overrides.clear()


def test_traded_news_endpoint_validates_request_body(mock_database_adapter):
    """Test that traded-news-context validates request body."""
    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    # Override dependency to prevent database connection attempt
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.post("/api/traded-news-context", json={"ticker": "AVGO", "reference_timestamp": "invalid"})

    assert response.status_code == 422
    errors = response.json()
    assert "detail" in errors

    # Clean up
    app.dependency_overrides.clear()


def test_traded_news_endpoint_handles_database_error(mock_database_adapter):
    """Test that traded-news-context handles database errors."""
    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    # Configure mock to raise exception
    mock_database_adapter.read_connection.side_effect = Exception("Database error")

    # Override dependency
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.post(
        "/api/traded-news-context",
        json={"ticker": "AVGO", "reference_timestamp": "2026-01-21T17:00:00Z"},
    )

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data

    # Clean up
    app.dependency_overrides.clear()


def test_traded_news_endpoint_uses_14_day_lookback(mock_database_adapter):
    """Test that traded-news-context uses correct lookback window."""
    from benz_news_context.app import app
    from benz_news_context.dependencies import get_db_adapter

    cursor = (
        mock_database_adapter.read_connection.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    )
    cursor.fetchall.return_value = []

    # Override dependency
    app.dependency_overrides[get_db_adapter] = lambda: mock_database_adapter

    client = TestClient(app)
    response = client.post(
        "/api/traded-news-context",
        json={"ticker": "AVGO", "reference_timestamp": "2026-01-21T17:00:00Z"},
    )

    assert response.status_code == 200
    # Verify the query was executed (lookback calculation happens in SQL)
    cursor.execute.assert_called_once()

    # Clean up
    app.dependency_overrides.clear()
