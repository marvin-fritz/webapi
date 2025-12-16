"""Pydantic schemas for News."""

from datetime import datetime

from pydantic import BaseModel, Field


class Stats(BaseModel):
    """Schema for news statistics."""
    
    likes: int = 0
    shares: int = 0
    views: int = 0


class NewsBase(BaseModel):
    """Base schema for News."""
    
    link: str
    category: str  # COMPANIES, ECONOMY, TECHNOLOGY, etc.
    description: str | None = None
    image: str | None = None
    pubDate: datetime
    source: str  # Source URL
    sourceId: str  # MongoDB ObjectId of the NewsSource as string
    sourceName: str
    stats: Stats = Field(default_factory=Stats)
    title: str


class NewsCreate(NewsBase):
    """Schema for creating a News item."""
    pass


class NewsUpdate(BaseModel):
    """Schema for updating a News item. All fields optional."""
    
    link: str | None = None
    category: str | None = None
    description: str | None = None
    image: str | None = None
    pubDate: datetime | None = None
    source: str | None = None
    sourceId: str | None = None
    sourceName: str | None = None
    stats: Stats | None = None
    title: str | None = None


class NewsResponse(NewsBase):
    """Schema for News response with ID and timestamps."""
    
    id: str = Field(..., description="MongoDB ObjectId as string")
    createdAt: datetime
    
    class Config:
        from_attributes = True
