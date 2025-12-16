"""Database configuration and session management for MongoDB."""

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import get_settings

# MongoDB client instance
_client: AsyncIOMotorClient | None = None


async def init_db() -> None:
    """Initialize MongoDB connection and Beanie ODM."""
    global _client
    settings = get_settings()
    
    _client = AsyncIOMotorClient(settings.mongodb_url)
    database = _client[settings.mongodb_database]
    
    # Import document models here to avoid circular imports
    from app.models.insider_trade import InsiderTrade
    from app.models.news import News
    from app.models.news_source import NewsSource
    from app.models.sec_financial import SECFinancial
    from app.models.stock_index import StockIndex
    
    await init_beanie(
        database=database,
        document_models=[News, NewsSource, InsiderTrade, SECFinancial, StockIndex],
    )


async def close_db() -> None:
    """Close MongoDB connection."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_client() -> AsyncIOMotorClient | None:
    """Get the MongoDB client instance."""
    return _client
