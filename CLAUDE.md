<!--
This CLAUDE.md file follows the benz ecosystem three-tier documentation pattern.
Created: 2026-01-28
-->

# benz_news_context - News Context Service - Repository-Specific Instructions

## Service Overview

This is a REST API service that provides prior news context about tickers to help determine if incoming news is derivative or irrelevant. The service exposes two endpoints that query the shared Supabase database to return recent news history and previously traded articles for a given ticker.

**Key Capabilities:**
- Retrieve recent news articles about a ticker (48-hour lookback)
- Retrieve news articles that resulted in executed trades (14-day lookback)
- Provide context for derivative news detection
- Help identify already-traded stories

**API Endpoints:**
- `POST /api/prior-news-context` - Returns recent news articles with sentiment and trade information
- `POST /api/traded-news-context` - Returns news articles that resulted in executed trades
- `GET /health` - Health check with database connection validation

## Database Access

**When working with PostgreSQL/Supabase databases**, invoke the appropriate ecosystem-wide skill:

- **Local development**: Use `benz-postgres-local` skill (Docker, 17-column schema, full features)
- **Cloud/Production**: Use `benz-postgres-supabase` skill (Supabase, 8-column schema, production/staging)

**DO NOT** make assumptions about table names, schemas, or data structures. **ALWAYS** consult the skills for:
- Table names (e.g., `news_articles`, `trading_decisions`, `order_submissions`, `order_fills`)
- Column names and data types
- Ticker formats (`["AAPL"]` vs `[{"symbol":"AAPL"}]`)
- Timestamp handling (TIMESTAMPTZ vs TIMESTAMP)
- JSONB metadata structure

**Key Tables Used by This Service:**
- `news_articles` - Article metadata (title, published_utc, tickers, channels, tags)
- `trading_decisions` - Per-ticker sentiment analysis and trading decisions
- `order_submissions` - Links articles to trade orders
- `order_fills` - Trade execution records

Skills accessible from `~/.claude/skills/` (ecosystem-wide, version-controlled in benz_mgmt).

## Cross-Repository Work

For architectural and system knowledge about this repository, invoke the `news-context-expert` skill (when available) which provides comprehensive understanding of context retrieval patterns. For tasks spanning multiple benz ecosystem repositories, use the `cross-repo-helper` agent in benz_mgmt. Agents and slash commands automatically invoke skills when deep system knowledge is needed.

## Task Tracking with Beads

This repository uses the `beads` MCP server for task tracking and dependency management.

**Common Commands:**
- `mcp__beads__list` - List all issues with optional filters
- `mcp__beads__create` - Create new issue (bug, feature, task, epic, chore)
- `mcp__beads__show` - Show detailed information about an issue
- `mcp__beads__update` - Update issue status, priority, or assignee
- `mcp__beads__ready` - Find tasks ready to work on (no blockers)
- `mcp__beads__blocked` - Get blocked issues and their dependencies

**Workflow:**
1. Set workspace context: `mcp__beads__set_context` with workspace_root
2. Create issues for new work with `mcp__beads__create`
3. Claim work by updating status to `in_progress`
4. Close issues when complete with `mcp__beads__close`

See `benz_mgmt` for ecosystem-wide task tracking patterns.

## Architecture

**Technology Stack:**
- FastAPI - REST API framework
- Uvicorn - ASGI server
- Pydantic - Data validation and serialization
- psycopg - PostgreSQL database adapter
- benz_common - Shared database connection utilities

**Configuration Pattern:**
- Module-level configuration (not Pydantic BaseSettings)
- Environment variables via `benz_common.db` pattern
- Dependency injection for database adapters

**Database Connection:**
- Uses `benz_common.db.get_database_adapter()` for connections
- Automatic pooler URL construction from environment variables
- Read-only connections via `db.read_connection()`

## Environment Variables

Uses `benz_common.db` environment variable pattern:

```bash
# Supabase Database
SUPABASE_PROD_URL=https://<project-ref>.supabase.co
SUPABASE_PROD_DB_PASSWORD=<database_password>

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Development

**Project Structure:**
```
benz_news_context/
├── src/benz_news_context/
│   ├── app.py                # FastAPI application
│   ├── config.py             # Environment configuration
│   ├── models.py             # Pydantic request/response models
│   ├── dependencies.py       # FastAPI dependencies
│   ├── db/
│   │   └── queries.py        # SQL query definitions
│   └── routers/
│       └── context.py        # API endpoint handlers
└── tests/
    ├── conftest.py           # Pytest fixtures
    ├── test_app.py
    ├── test_models.py
    └── test_queries.py
```

**Common Commands:**
- `make install` - Install dependencies with uv
- `make dev` - Start development server
- `make test` - Run tests
- `make test-cov` - Run tests with coverage
- `make lint` - Run linters
- `make format` - Format code

## Integration with benz_analyzer

The `benz_analyzer` service can call these endpoints to enrich its analysis and determine if incoming news is derivative or already traded.

**Usage Pattern:**
```python
import httpx

NEWS_CONTEXT_BASE_URL = os.environ.get("NEWS_CONTEXT_URL", "http://localhost:8000")

async def get_prior_context(ticker: str, reference_ts: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NEWS_CONTEXT_BASE_URL}/api/prior-news-context",
            json={"ticker": ticker, "reference_timestamp": reference_ts}
        )
        return response.json()
```
