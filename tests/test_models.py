"""Tests for Pydantic request/response models."""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError


def test_prior_news_request_validates_required_fields():
    """Test that PriorNewsRequest requires ticker and reference_timestamp."""
    from benz_news_context.models import PriorNewsRequest

    with pytest.raises(ValidationError) as exc_info:
        PriorNewsRequest.model_validate({})

    errors = exc_info.value.errors()
    error_fields = {error["loc"][0] for error in errors}
    assert "ticker" in error_fields
    assert "reference_timestamp" in error_fields


def test_prior_news_request_accepts_valid_data():
    """Test that PriorNewsRequest accepts valid data and parses datetime."""
    from benz_news_context.models import PriorNewsRequest

    data = {"ticker": "AVGO", "reference_timestamp": "2026-01-21T17:00:00Z"}
    request = PriorNewsRequest.model_validate(data)

    assert request.ticker == "AVGO"
    assert isinstance(request.reference_timestamp, datetime)
    assert request.reference_timestamp.tzinfo is not None


def test_prior_news_request_validates_timestamp_format():
    """Test that PriorNewsRequest rejects invalid timestamp format."""
    from benz_news_context.models import PriorNewsRequest

    with pytest.raises(ValidationError) as exc_info:
        PriorNewsRequest.model_validate({"ticker": "AVGO", "reference_timestamp": "invalid"})

    errors = exc_info.value.errors()
    assert any("reference_timestamp" in str(error["loc"]) for error in errors)


def test_prior_news_article_accepts_dict_row():
    """Test that PriorNewsArticle can be created from psycopg dict_row."""
    from benz_news_context.models import PriorNewsArticle

    dict_row = {
        "id": "uuid-1234",
        "title": "Test Article",
        "published_utc": datetime(2026, 1, 20, 14, 30, 0, tzinfo=timezone.utc),
        "channels": ["technology"],
        "tags": ["earnings"],
        "sentiment": "bullish",
        "sentiment_score": 0.85,
        "was_traded": True,
        "trade_side": "buy",
    }

    article = PriorNewsArticle(**dict_row)

    assert article.id == "uuid-1234"
    assert article.title == "Test Article"
    assert article.sentiment == "bullish"
    assert article.sentiment_score == 0.85
    assert article.was_traded is True
    assert article.trade_side == "buy"


def test_prior_news_article_model_serialization():
    """Test that PriorNewsArticle serializes to snake_case dict."""
    from benz_news_context.models import PriorNewsArticle

    article = PriorNewsArticle(
        id="uuid-1234",
        title="Test Article",
        published_utc=datetime(2026, 1, 20, 14, 30, 0, tzinfo=timezone.utc),
        channels=["technology"],
        tags=["earnings"],
        sentiment="bullish",
        sentiment_score=0.85,
        was_traded=True,
        trade_side="buy",
    )

    serialized = article.model_dump()

    assert "id" in serialized
    assert "title" in serialized
    assert "published_utc" in serialized
    assert "channels" in serialized
    assert "tags" in serialized
    assert "sentiment" in serialized
    assert "sentiment_score" in serialized
    assert "was_traded" in serialized
    assert "trade_side" in serialized


def test_prior_news_article_handles_nullable_fields():
    """Test that PriorNewsArticle handles null values for optional fields."""
    from benz_news_context.models import PriorNewsArticle

    article = PriorNewsArticle(
        id="uuid-1234",
        title="Test Article",
        published_utc=datetime(2026, 1, 20, 14, 30, 0, tzinfo=timezone.utc),
        channels=["technology"],
        tags=["earnings"],
        sentiment=None,
        sentiment_score=None,
        was_traded=False,
        trade_side=None,
    )

    serialized = article.model_dump()

    # Nullable fields should be present with None values, not missing
    assert "sentiment" in serialized
    assert serialized["sentiment"] is None
    assert "sentiment_score" in serialized
    assert serialized["sentiment_score"] is None
    assert "trade_side" in serialized
    assert serialized["trade_side"] is None


def test_prior_news_response_serialization():
    """Test that PriorNewsResponse serializes correctly."""
    from benz_news_context.models import PriorNewsArticle, PriorNewsResponse

    article = PriorNewsArticle(
        id="uuid-1234",
        title="Test Article",
        published_utc=datetime(2026, 1, 20, 14, 30, 0, tzinfo=timezone.utc),
        channels=["technology"],
        tags=["earnings"],
        sentiment="bullish",
        sentiment_score=0.85,
        was_traded=True,
        trade_side="buy",
    )

    response = PriorNewsResponse(
        ticker="AVGO",
        reference_timestamp=datetime(2026, 1, 21, 17, 0, 0, tzinfo=timezone.utc),
        lookback_hours=48,
        articles=[article],
        article_count=1,
    )

    serialized = response.model_dump()

    assert serialized["ticker"] == "AVGO"
    assert serialized["lookback_hours"] == 48
    assert len(serialized["articles"]) == 1
    assert serialized["article_count"] == 1


def test_traded_news_request_validates_required_fields():
    """Test that TradedNewsRequest requires ticker and reference_timestamp."""
    from benz_news_context.models import TradedNewsRequest

    with pytest.raises(ValidationError) as exc_info:
        TradedNewsRequest.model_validate({})

    errors = exc_info.value.errors()
    error_fields = {error["loc"][0] for error in errors}
    assert "ticker" in error_fields
    assert "reference_timestamp" in error_fields


def test_traded_news_request_accepts_valid_data():
    """Test that TradedNewsRequest accepts valid data."""
    from benz_news_context.models import TradedNewsRequest

    data = {"ticker": "AVGO", "reference_timestamp": "2026-01-21T17:00:00Z"}
    request = TradedNewsRequest.model_validate(data)

    assert request.ticker == "AVGO"
    assert isinstance(request.reference_timestamp, datetime)


def test_traded_news_trade_accepts_dict_row():
    """Test that TradedNewsTrade can be created from psycopg dict_row."""
    from benz_news_context.models import TradedNewsTrade

    dict_row = {
        "article_id": "uuid-5678",
        "title": "Broadcom Q4 Earnings Beat Expectations",
        "published_utc": datetime(2026, 1, 15, 16, 5, 0, tzinfo=timezone.utc),
        "trade_executed_at": datetime(2026, 1, 15, 16, 5, 32, tzinfo=timezone.utc),
        "side": "buy",
        "fill_price": 245.67,
    }

    trade = TradedNewsTrade(**dict_row)

    assert trade.article_id == "uuid-5678"
    assert trade.title == "Broadcom Q4 Earnings Beat Expectations"
    assert trade.side == "buy"
    assert trade.fill_price == 245.67


def test_traded_news_trade_model_serialization():
    """Test that TradedNewsTrade serializes correctly."""
    from benz_news_context.models import TradedNewsTrade

    trade = TradedNewsTrade(
        article_id="uuid-5678",
        title="Test Trade Article",
        published_utc=datetime(2026, 1, 15, 16, 5, 0, tzinfo=timezone.utc),
        trade_executed_at=datetime(2026, 1, 15, 16, 5, 32, tzinfo=timezone.utc),
        side="buy",
        fill_price=245.67,
    )

    serialized = trade.model_dump()

    assert "article_id" in serialized
    assert "title" in serialized
    assert "published_utc" in serialized
    assert "trade_executed_at" in serialized
    assert "side" in serialized
    assert "fill_price" in serialized


def test_traded_news_response_serialization():
    """Test that TradedNewsResponse serializes correctly."""
    from benz_news_context.models import TradedNewsResponse, TradedNewsTrade

    trade = TradedNewsTrade(
        article_id="uuid-5678",
        title="Test Trade Article",
        published_utc=datetime(2026, 1, 15, 16, 5, 0, tzinfo=timezone.utc),
        trade_executed_at=datetime(2026, 1, 15, 16, 5, 32, tzinfo=timezone.utc),
        side="buy",
        fill_price=245.67,
    )

    response = TradedNewsResponse(
        ticker="AVGO",
        reference_timestamp=datetime(2026, 1, 21, 17, 0, 0, tzinfo=timezone.utc),
        lookback_days=14,
        trades=[trade],
        trade_count=1,
    )

    serialized = response.model_dump()

    assert serialized["ticker"] == "AVGO"
    assert serialized["lookback_days"] == 14
    assert len(serialized["trades"]) == 1
    assert serialized["trade_count"] == 1
