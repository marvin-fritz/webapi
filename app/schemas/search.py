"""Pydantic schemas for Search functionality."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SearchResultType(str, Enum):
    """Types of search results."""
    
    STOCK = "stock"
    NEWS = "news"
    # Erweiterbar: INSIDER_TRADE = "insider_trade", COMPANY = "company", etc.


class SearchResultAction(BaseModel):
    """Action to perform when clicking on a search result."""
    
    type: str  # "redirect", "modal", etc.
    url: str  # Target URL


class BaseSearchResult(BaseModel):
    """Base schema for a search result."""
    
    id: str
    type: SearchResultType
    title: str
    subtitle: str | None = None
    description: str | None = None
    image: str | None = None
    action: SearchResultAction
    relevanceScore: float = Field(default=0.0, description="Score indicating match relevance")
    metadata: dict | None = None


class StockSearchResult(BaseSearchResult):
    """Search result for a stock."""
    
    type: SearchResultType = SearchResultType.STOCK
    ticker: str | None = None
    isin: str | None = None
    exchangeCode: str | None = None


class NewsSearchResult(BaseSearchResult):
    """Search result for a news article."""
    
    type: SearchResultType = SearchResultType.NEWS
    source: str | None = None
    category: str | None = None
    pubDate: datetime | None = None


class SearchRequest(BaseModel):
    """Request schema for search."""
    
    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    types: list[SearchResultType] | None = Field(
        None,
        description="Filter by result types. If empty, search all types."
    )
    limit: int = Field(default=10, ge=1, le=50, description="Max results per type")


class SearchResponse(BaseModel):
    """Response schema for search."""
    
    query: str
    totalResults: int
    results: list[BaseSearchResult]
    resultsByType: dict[str, int] = Field(
        default_factory=dict,
        description="Count of results per type"
    )
