"""REST API endpoints for Search functionality."""

from fastapi import APIRouter, Query

from app.schemas.search import (
    BaseSearchResult,
    SearchResponse,
    SearchResultType,
)
from app.services.search import SearchService

router = APIRouter()


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    types: list[SearchResultType] | None = Query(
        None,
        description="Filter by result types (stock, news). If not provided, searches all."
    ),
    limit: int = Query(10, ge=1, le=50, description="Maximum results per type"),
) -> SearchResponse:
    """
    Unified search across multiple collections.
    
    Searches through:
    - **Stocks**: By name, ticker, or ISIN
    - **News**: By title or description
    
    Results include an `action` field with redirect information:
    - Stocks redirect to: `https://finanz-copilot.de/stock/{isin}`
    - News redirect to the original article URL
    
    Results are sorted by relevance score.
    
    **Examples:**
    - `/api/v1/search?q=Apple` - Search all types for "Apple"
    - `/api/v1/search?q=AAPL&types=stock` - Search only stocks
    - `/api/v1/search?q=Tesla&types=stock&types=news` - Search stocks and news
    """
    results = await SearchService.search(
        query=q,
        types=types,
        limit=limit,
    )
    
    # Count results by type
    results_by_type: dict[str, int] = {}
    for result in results:
        type_str = result.type.value
        results_by_type[type_str] = results_by_type.get(type_str, 0) + 1
    
    return SearchResponse(
        query=q,
        totalResults=len(results),
        results=results,
        resultsByType=results_by_type,
    )


@router.get("/stocks", response_model=list[BaseSearchResult])
async def search_stocks(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
) -> list[BaseSearchResult]:
    """
    Search only in stocks.
    
    Shortcut for `/api/v1/search?q={query}&types=stock`
    """
    return await SearchService.search(
        query=q,
        types=[SearchResultType.STOCK],
        limit=limit,
    )


@router.get("/news", response_model=list[BaseSearchResult])
async def search_news(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
) -> list[BaseSearchResult]:
    """
    Search only in news.
    
    Shortcut for `/api/v1/search?q={query}&types=news`
    """
    return await SearchService.search(
        query=q,
        types=[SearchResultType.NEWS],
        limit=limit,
    )
