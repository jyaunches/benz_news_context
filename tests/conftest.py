"""Pytest fixtures for benz_news_context tests."""
import os
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_database_adapter():
    """Mock DatabaseAdapter for testing without database connection."""
    adapter = MagicMock()
    cursor = MagicMock()

    # Mock fetchall to return empty results by default
    cursor.fetchall.return_value = []
    cursor.execute.return_value = None

    connection = MagicMock()
    # Mock cursor() to accept row_factory parameter and return cursor context manager
    connection.cursor.return_value.__enter__.return_value = cursor
    connection.cursor.return_value.__exit__.return_value = None

    # Mock read_connection() context manager
    adapter.read_connection.return_value.__enter__.return_value = connection
    adapter.read_connection.return_value.__exit__.return_value = None

    return adapter


@pytest.fixture
def mock_env_vars():
    """Set environment variables for testing and restore after."""
    original_env = {
        "ENVIRONMENT": os.getenv("ENVIRONMENT"),
        "SUPABASE_PROD_URL": os.getenv("SUPABASE_PROD_URL"),
        "SUPABASE_PROD_DB_PASSWORD": os.getenv("SUPABASE_PROD_DB_PASSWORD"),
    }

    # Set test values
    os.environ["ENVIRONMENT"] = "test"
    os.environ["SUPABASE_PROD_URL"] = "https://test.supabase.co"
    os.environ["SUPABASE_PROD_DB_PASSWORD"] = "test_password"

    yield

    # Restore original values
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
