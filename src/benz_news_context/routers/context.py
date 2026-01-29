"""API endpoints for news context retrieval."""
from benz_common.db import DatabaseAdapter
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from psycopg2.extras import RealDictCursor

from ..db.queries import PRIOR_NEWS_QUERY, TRADED_NEWS_QUERY
from ..dependencies import get_db_adapter
from ..models import (
    PriorNewsArticle,
    PriorNewsRequest,
    PriorNewsResponse,
    TradedNewsRequest,
    TradedNewsResponse,
    TradedNewsTrade,
)

router = APIRouter()


@router.post("/api/prior-news-context", response_model=PriorNewsResponse)
async def prior_news_context(
    request: PriorNewsRequest,
    db: DatabaseAdapter = Depends(get_db_adapter),
):
    """Return recent news articles about a ticker from the 48 hours before a reference timestamp."""
    try:
        with db.read_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(PRIOR_NEWS_QUERY, (request.ticker, request.reference_timestamp))
                rows = cur.fetchall()
                articles = [PriorNewsArticle(**dict(row)) for row in rows]

        return PriorNewsResponse(
            ticker=request.ticker,
            reference_timestamp=request.reference_timestamp,
            lookback_hours=48,
            articles=articles,
            article_count=len(articles),
        )
    except Exception as e:
        logger.error(
            f"Database error for prior-news-context: ticker={request.ticker}, "
            f"ref_ts={request.reference_timestamp}, error={type(e).__name__}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/api/traded-news-context", response_model=TradedNewsResponse)
async def traded_news_context(
    request: TradedNewsRequest,
    db: DatabaseAdapter = Depends(get_db_adapter),
):
    """Return news articles that resulted in executed trades within 14 days before a reference timestamp."""
    try:
        with db.read_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(TRADED_NEWS_QUERY, (request.ticker, request.reference_timestamp))
                rows = cur.fetchall()
                trades = [TradedNewsTrade(**dict(row)) for row in rows]

        return TradedNewsResponse(
            ticker=request.ticker,
            reference_timestamp=request.reference_timestamp,
            lookback_days=14,
            trades=trades,
            trade_count=len(trades),
        )
    except Exception as e:
        logger.error(
            f"Database error for traded-news-context: ticker={request.ticker}, "
            f"ref_ts={request.reference_timestamp}, error={type(e).__name__}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")
