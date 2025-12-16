"""Service for NewsSource CRUD operations."""

from beanie import PydanticObjectId

from app.models.news_source import NewsSource
from app.schemas.news_source import NewsSourceCreate, NewsSourceUpdate


class NewsSourceService:
    """Service class for NewsSource operations."""
    
    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100) -> list[NewsSource]:
        """Get all news sources with pagination."""
        return await NewsSource.find_all().skip(skip).limit(limit).to_list()
    
    @staticmethod
    async def get_by_id(id: str) -> NewsSource | None:
        """Get a news source by ID."""
        try:
            return await NewsSource.get(PydanticObjectId(id))
        except Exception:
            return None
    
    @staticmethod
    async def create(data: NewsSourceCreate) -> NewsSource:
        """Create a new news source."""
        news_source = NewsSource(**data.model_dump())
        await news_source.insert()
        return news_source
    
    @staticmethod
    async def update(id: str, data: NewsSourceUpdate) -> NewsSource | None:
        """Update an existing news source."""
        news_source = await NewsSourceService.get_by_id(id)
        if news_source is None:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(news_source, key, value)
        
        await news_source.save()
        return news_source
    
    @staticmethod
    async def delete(id: str) -> bool:
        """Delete a news source by ID."""
        news_source = await NewsSourceService.get_by_id(id)
        if news_source is None:
            return False
        
        await news_source.delete()
        return True
    
    @staticmethod
    async def count() -> int:
        """Get the total count of news sources."""
        return await NewsSource.count()
