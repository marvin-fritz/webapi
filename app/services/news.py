"""Service for News CRUD operations."""

from beanie import PydanticObjectId

from app.models.news import News
from app.schemas.news import NewsCreate, NewsUpdate


class NewsService:
    """Service class for News operations."""
    
    @staticmethod
    async def get_all(
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        source_id: str | None = None,
    ) -> list[News]:
        """Get all news with pagination and optional filtering."""
        query = {}
        
        if category:
            query["category"] = category
        if source_id:
            try:
                query["sourceId"] = PydanticObjectId(source_id)
            except Exception:
                pass  # Invalid ObjectId, skip filter
        
        return await News.find(query).skip(skip).limit(limit).sort("-pubDate").to_list()
    
    @staticmethod
    async def get_by_id(id: str) -> News | None:
        """Get a news item by ID."""
        try:
            return await News.get(PydanticObjectId(id))
        except Exception:
            return None
    
    @staticmethod
    async def create(data: NewsCreate) -> News:
        """Create a new news item."""
        news_data = data.model_dump()
        # Convert sourceId string to PydanticObjectId
        if "sourceId" in news_data and isinstance(news_data["sourceId"], str):
            news_data["sourceId"] = PydanticObjectId(news_data["sourceId"])
        
        news = News(**news_data)
        await news.insert()
        return news
    
    @staticmethod
    async def update(id: str, data: NewsUpdate) -> News | None:
        """Update an existing news item."""
        news = await NewsService.get_by_id(id)
        if news is None:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        # Convert sourceId string to PydanticObjectId if present
        if "sourceId" in update_data and isinstance(update_data["sourceId"], str):
            update_data["sourceId"] = PydanticObjectId(update_data["sourceId"])
        
        for key, value in update_data.items():
            setattr(news, key, value)
        
        await news.save()
        return news
    
    @staticmethod
    async def delete(id: str) -> bool:
        """Delete a news item by ID."""
        news = await NewsService.get_by_id(id)
        if news is None:
            return False
        
        await news.delete()
        return True
    
    @staticmethod
    async def count(
        category: str | None = None,
        source_id: str | None = None,
    ) -> int:
        """Get the total count of news items with optional filtering."""
        query = {}
        
        if category:
            query["category"] = category
        if source_id:
            try:
                query["sourceId"] = PydanticObjectId(source_id)
            except Exception:
                pass
        
        return await News.find(query).count()
