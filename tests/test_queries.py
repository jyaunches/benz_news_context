"""Tests for SQL query definitions."""


def test_prior_news_query_structure():
    """Test that PRIOR_NEWS_QUERY contains required columns."""
    from benz_news_context.db.queries import PRIOR_NEWS_QUERY

    # Check for required columns in SELECT clause
    required_columns = [
        "id",
        "title",
        "published_utc",
        "channels",
        "tags",
        "sentiment",
        "sentiment_score",
        "was_traded",
        "trade_side",
    ]

    for column in required_columns:
        assert column in PRIOR_NEWS_QUERY.lower(), f"Missing column: {column}"


def test_prior_news_query_parameters():
    """Test that PRIOR_NEWS_QUERY uses parameterized queries."""
    from benz_news_context.db.queries import PRIOR_NEWS_QUERY

    # Check for PostgreSQL parameter placeholders
    assert "$1" in PRIOR_NEWS_QUERY, "Missing $1 parameter (ticker)"
    assert "$2" in PRIOR_NEWS_QUERY, "Missing $2 parameter (reference_timestamp)"


def test_traded_news_query_structure():
    """Test that TRADED_NEWS_QUERY contains required columns."""
    from benz_news_context.db.queries import TRADED_NEWS_QUERY

    # Check for required columns
    required_columns = [
        "article_id",
        "title",
        "published_utc",
        "trade_executed_at",
        "side",
        "fill_price",
    ]

    for column in required_columns:
        assert column in TRADED_NEWS_QUERY.lower(), f"Missing column: {column}"


def test_traded_news_query_parameters():
    """Test that TRADED_NEWS_QUERY uses parameterized queries."""
    from benz_news_context.db.queries import TRADED_NEWS_QUERY

    # Check for PostgreSQL parameter placeholders
    assert "$1" in TRADED_NEWS_QUERY, "Missing $1 parameter (ticker)"
    assert "$2" in TRADED_NEWS_QUERY, "Missing $2 parameter (reference_timestamp)"
