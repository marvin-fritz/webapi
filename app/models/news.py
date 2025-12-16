"""Beanie Document model for News collection."""

from datetime import datetime, timezone

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class Stats(BaseModel):
    """Embedded document for news statistics."""
    
    likes: int = 0
    shares: int = 0
    views: int = 0


class News(Document):
    """Document model for the news collection."""
    
    link: str
    category: str  # COMPANIES, ECONOMY, TECHNOLOGY, etc.
    description: str | None = None
    image: str | None = None
    pubDate: datetime
    source: str  # Source URL
    sourceId: PydanticObjectId  # Reference to NewsSource
    sourceName: str
    stats: Stats = Field(default_factory=Stats)
    title: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "news"  # MongoDB collection name
        use_state_management = True
