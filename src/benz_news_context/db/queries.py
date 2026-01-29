"""SQL query definitions for benz_news_context service."""

PRIOR_NEWS_QUERY = """
SELECT
    na.id,
    na.title,
    na.published_utc,
    na.channels,
    na.tags,
    td.sentiment,
    td.confidence AS sentiment_score,
    (td.decision = 'TRADE') AS was_traded,
    CASE WHEN td.decision = 'TRADE' THEN
        (SELECT os.side FROM order_submissions os WHERE os.article_id = na.id AND os.ticker = $1 LIMIT 1)
    ELSE NULL END AS trade_side
FROM news_articles na
LEFT JOIN trading_decisions td
    ON na.id = td.article_id AND td.ticker = $1
WHERE $1 = ANY(na.tickers)
  AND na.published_utc >= ($2::timestamptz - INTERVAL '48 hours')
  AND na.published_utc < $2::timestamptz
ORDER BY na.published_utc DESC;
"""

TRADED_NEWS_QUERY = """
SELECT
    na.id AS article_id,
    na.title,
    na.published_utc,
    of.filled_at AS trade_executed_at,
    os.side,
    of.fill_price
FROM news_articles na
INNER JOIN order_submissions os
    ON na.id = os.article_id
INNER JOIN order_fills of
    ON os.client_order_id = of.client_order_id
WHERE os.symbol = $1
  AND of.order_leg = 'entry'
  AND of.filled_at >= ($2::timestamptz - INTERVAL '14 days')
  AND of.filled_at < $2::timestamptz
ORDER BY of.filled_at DESC;
"""
