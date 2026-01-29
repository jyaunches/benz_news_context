"""FastAPI application for benz_news_context service."""
from fastapi import FastAPI

app = FastAPI(
    title="benz_news_context",
    description="REST API service providing prior news context for derivative news detection",
    version="0.1.0",
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
