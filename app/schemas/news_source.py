"""Pydantic schemas for NewsSource."""

from pydantic import BaseModel, Field


class Feed(BaseModel):
    """Schema for a news feed within a source."""
    
    link: str
    category: str  # COMPANIES, ECONOMY, TECHNOLOGY, etc.
    hasImage: bool = Field(alias="hasImage", default=False)
    
    class Config:
        populate_by_name = True


class NewsSourceBase(BaseModel):
    """Base schema for NewsSource."""
    
    name: str
    feeds: list[Feed] = []
    logo: str | None = None
    link: str
    language: str = "DE"  # DE, EN, etc.
    paywall: bool = False


class NewsSourceCreate(NewsSourceBase):
    """Schema for creating a NewsSource."""
    pass


class NewsSourceUpdate(BaseModel):
    """Schema for updating a NewsSource. All fields optional."""
    
    name: str | None = None
    feeds: list[Feed] | None = None
    logo: str | None = None
    link: str | None = None
    language: str | None = None
    paywall: bool | None = None


class NewsSourceResponse(NewsSourceBase):
    """Schema for NewsSource response with ID."""
    
    id: str = Field(..., description="MongoDB ObjectId as string")
    
    class Config:
        from_attributes = True
