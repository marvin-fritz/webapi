"""Beanie Document model for NewsSource collection."""

from beanie import Document
from pydantic import Field


class Feed(Document):
    """Embedded document for a news feed within a source."""
    
    link: str
    category: str  # COMPANIES, ECONOMY, TECHNOLOGY, etc.
    hasImage: bool = Field(alias="hasImage", default=False)
    
    class Settings:
        # This is an embedded document, not a standalone collection
        pass


class NewsSource(Document):
    """Document model for the newsSources collection."""
    
    name: str
    feeds: list[Feed] = []
    logo: str | None = None
    link: str
    language: str = "DE"  # DE, EN, etc.
    paywall: bool = False
    
    class Settings:
        name = "newsSources"  # MongoDB collection name
        use_state_management = True
