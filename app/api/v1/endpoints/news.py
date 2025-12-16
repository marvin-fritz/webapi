"""REST API endpoints for News."""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.news import NewsCreate, NewsResponse, NewsUpdate
from app.services.news import NewsService

router = APIRouter()


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
    return [
        NewsResponse(
            id=str(item.id),
            link=item.link,
            category=item.category,
            description=item.description,
            image=item.image,
            pubDate=item.pubDate,
            source=item.source,
            sourceId=str(item.sourceId),
            sourceName=item.sourceName,
            stats=item.stats,
            title=item.title,
            createdAt=item.createdAt,
        )
        for item in news_items
    ]


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(news_id: str) -> NewsResponse:
    """Get a news item by ID."""
    news = await NewsService.get_by_id(news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    
    return NewsResponse(
        id=str(news.id),
        link=news.link,
        category=news.category,
        description=news.description,
        image=news.image,
        pubDate=news.pubDate,
        source=news.source,
        sourceId=str(news.sourceId),
        sourceName=news.sourceName,
        stats=news.stats,
        title=news.title,
        createdAt=news.createdAt,
    )


@router.post("", response_model=NewsResponse, status_code=201)
async def create_news(data: NewsCreate) -> NewsResponse:
    """Create a new news item."""
    news = await NewsService.create(data)
    
    return NewsResponse(
        id=str(news.id),
        link=news.link,
        category=news.category,
        description=news.description,
        image=news.image,
        pubDate=news.pubDate,
        source=news.source,
        sourceId=str(news.sourceId),
        sourceName=news.sourceName,
        stats=news.stats,
        title=news.title,
        createdAt=news.createdAt,
    )


@router.put("/{news_id}", response_model=NewsResponse)
async def update_news(news_id: str, data: NewsUpdate) -> NewsResponse:
    """Update an existing news item."""
    news = await NewsService.update(news_id, data)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    
    return NewsResponse(
        id=str(news.id),
        link=news.link,
        category=news.category,
        description=news.description,
        image=news.image,
        pubDate=news.pubDate,
        source=news.source,
        sourceId=str(news.sourceId),
        sourceName=news.sourceName,
        stats=news.stats,
        title=news.title,
        createdAt=news.createdAt,
    )


@router.delete("/{news_id}", status_code=204)
async def delete_news(news_id: str) -> None:
    """Delete a news item by ID."""
    deleted = await NewsService.delete(news_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="News not found")
