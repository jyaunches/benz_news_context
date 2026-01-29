"""FastAPI application for benz_news_context service."""
from benz_common.db import DatabaseAdapter
from fastapi import Depends, FastAPI, HTTPException

from .dependencies import get_db_adapter
from .routers import context

app = FastAPI(
    title="benz_news_context",
    description="REST API service providing prior news context for derivative news detection",
    version="0.1.0",
)

# Register routers
app.include_router(context.router)


@app.get("/health")
async def health(db: DatabaseAdapter = Depends(get_db_adapter)):
    """Health check endpoint with database validation."""
    try:
        with db.read_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "database": "error", "error": str(e)},
        )
