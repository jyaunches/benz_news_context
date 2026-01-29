"""Pydantic models for benz_news_context API requests and responses."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# Request Models
class PriorNewsRequest(BaseModel):
    """Request model for /api/prior-news-context endpoint."""

    ticker: str
    reference_timestamp: datetime


class TradedNewsRequest(BaseModel):
    """Request model for /api/traded-news-context endpoint."""

    ticker: str
    reference_timestamp: datetime


# Response Models
class PriorNewsArticle(BaseModel):
    """Article with sentiment and trade information."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    published_utc: datetime
    channels: list[str]
    tags: list[str]
    sentiment: str | None = None
    sentiment_score: float | None = None
    was_traded: bool
    trade_side: str | None = None


class PriorNewsResponse(BaseModel):
    """Response model for /api/prior-news-context endpoint."""

    ticker: str
    reference_timestamp: datetime
    lookback_hours: int
    articles: list[PriorNewsArticle]
    article_count: int


class TradedNewsTrade(BaseModel):
    """Trade execution details for a news article."""

    article_id: str
    title: str
    published_utc: datetime
    trade_executed_at: datetime
    side: str
    fill_price: float


class TradedNewsResponse(BaseModel):
    """Response model for /api/traded-news-context endpoint."""

    ticker: str
    reference_timestamp: datetime
    lookback_days: int
    trades: list[TradedNewsTrade]
    trade_count: int
