"""Entry point for running the benz_news_context service."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "benz_news_context.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
