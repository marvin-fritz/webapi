"""REST API endpoints for NewsSource."""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.news_source import (
    NewsSourceCreate,
    NewsSourceResponse,
    NewsSourceUpdate,
)
from app.services.news_source import NewsSourceService

router = APIRouter()


@router.get("", response_model=list[NewsSourceResponse])
async def get_all_news_sources(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
) -> list[NewsSourceResponse]:
    """Get all news sources with pagination."""
    sources = await NewsSourceService.get_all(skip=skip, limit=limit)
    return [
        NewsSourceResponse(
            id=str(source.id),
            name=source.name,
            feeds=source.feeds,
            logo=source.logo,
            link=source.link,
            language=source.language,
            paywall=source.paywall,
        )
        for source in sources
    ]


@router.get("/{source_id}", response_model=NewsSourceResponse)
async def get_news_source(source_id: str) -> NewsSourceResponse:
    """Get a news source by ID."""
    source = await NewsSourceService.get_by_id(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="News source not found")
    
    return NewsSourceResponse(
        id=str(source.id),
        name=source.name,
        feeds=source.feeds,
        logo=source.logo,
        link=source.link,
        language=source.language,
        paywall=source.paywall,
    )


@router.post("", response_model=NewsSourceResponse, status_code=201)
async def create_news_source(data: NewsSourceCreate) -> NewsSourceResponse:
    """Create a new news source."""
    source = await NewsSourceService.create(data)
    
    return NewsSourceResponse(
        id=str(source.id),
        name=source.name,
        feeds=source.feeds,
        logo=source.logo,
        link=source.link,
        language=source.language,
        paywall=source.paywall,
    )


@router.put("/{source_id}", response_model=NewsSourceResponse)
async def update_news_source(
    source_id: str,
    data: NewsSourceUpdate,
) -> NewsSourceResponse:
    """Update an existing news source."""
    source = await NewsSourceService.update(source_id, data)
    if source is None:
        raise HTTPException(status_code=404, detail="News source not found")
    
    return NewsSourceResponse(
        id=str(source.id),
        name=source.name,
        feeds=source.feeds,
        logo=source.logo,
        link=source.link,
        language=source.language,
        paywall=source.paywall,
    )


@router.delete("/{source_id}", status_code=204)
async def delete_news_source(source_id: str) -> None:
    """Delete a news source by ID."""
    deleted = await NewsSourceService.delete(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="News source not found")
