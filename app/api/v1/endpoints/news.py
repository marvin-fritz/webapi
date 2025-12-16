"""REST API endpoints for News."""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.news import NewsCreate, NewsResponse, NewsUpdate, Stats
from app.services.news import NewsService

router = APIRouter()


def _news_to_response(item) -> NewsResponse:
    """Convert News document to response schema."""
    return NewsResponse(
        id=str(item.id),
        link=item.link,
        category=item.category,
        description=item.description,
        image=item.image,
        pubDate=item.pubDate,
        source=item.source,
        sourceId=str(item.sourceId),
        sourceName=item.sourceName,
        stats=Stats(
            likes=item.stats.likes if item.stats else 0,
            shares=item.stats.shares if item.stats else 0,
            views=item.stats.views if item.stats else 0,
        ) if item.stats else Stats(),
        title=item.title,
        createdAt=item.createdAt,
    )


@router.get("", response_model=list[NewsResponse])
async def get_all_news(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    category: str | None = Query(None, description="Filter by category"),
    source_id: str | None = Query(None, alias="sourceId", description="Filter by source ID"),
) -> list[NewsResponse]:
    """Get all news items with pagination and optional filtering."""
    news_items = await NewsService.get_all(
        skip=skip,
        limit=limit,
        category=category,
        source_id=source_id,
    )
    return [_news_to_response(item) for item in news_items]


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(news_id: str) -> NewsResponse:
    """Get a news item by ID."""
    news = await NewsService.get_by_id(news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    
    return _news_to_response(news)


@router.post("", response_model=NewsResponse, status_code=201)
async def create_news(data: NewsCreate) -> NewsResponse:
    """Create a new news item."""
    news = await NewsService.create(data)
    
    return _news_to_response(news)


@router.put("/{news_id}", response_model=NewsResponse)
async def update_news(news_id: str, data: NewsUpdate) -> NewsResponse:
    """Update an existing news item."""
    news = await NewsService.update(news_id, data)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    
    return _news_to_response(news)


@router.delete("/{news_id}", status_code=204)
async def delete_news(news_id: str) -> None:
    """Delete a news item by ID."""
    deleted = await NewsService.delete(news_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="News not found")
