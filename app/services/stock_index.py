"""Service for StockIndex CRUD operations."""

from datetime import datetime

from beanie import PydanticObjectId

from app.models.stock_index import StockIndex
from app.schemas.stock_index import StockIndexCreate, StockIndexUpdate


class StockIndexService:
    """Service class for StockIndex operations."""
    
    @staticmethod
    async def get_all(
        skip: int = 0,
        limit: int = 100,
        isin: str | None = None,
        ticker: str | None = None,
        exchange_code: str | None = None,
        security_type: str | None = None,
        name: str | None = None,
    ) -> list[StockIndex]:
        """Get all stocks with pagination and filtering."""
        query = {}
        
        if isin:
            query["isin"] = isin
        if ticker:
            query["ticker"] = {"$regex": f"^{ticker}", "$options": "i"}
        if exchange_code:
            query["exchangeCode"] = exchange_code
        if security_type:
            query["securityType"] = security_type
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        
        return await StockIndex.find(query).skip(skip).limit(limit).sort("name").to_list()
    
    @staticmethod
    async def get_by_id(id: str) -> StockIndex | None:
        """Get a stock by ID."""
        try:
            return await StockIndex.get(PydanticObjectId(id))
        except Exception:
            return None
    
    @staticmethod
    async def get_by_isin(isin: str) -> StockIndex | None:
        """Get a stock by ISIN."""
        return await StockIndex.find_one({"isin": isin})
    
    @staticmethod
    async def get_by_ticker(ticker: str) -> list[StockIndex]:
        """Get stocks by ticker (may return multiple for different exchanges)."""
        return await StockIndex.find({"ticker": ticker}).to_list()
    
    @staticmethod
    async def search(
        query: str,
        limit: int = 20,
    ) -> list[StockIndex]:
        """Search stocks by name or ticker."""
        return await StockIndex.find({
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"ticker": {"$regex": f"^{query}", "$options": "i"}},
                {"isin": {"$regex": f"^{query}", "$options": "i"}},
            ]
        }).limit(limit).to_list()
    
    @staticmethod
    async def create(data: StockIndexCreate) -> StockIndex:
        """Create a new stock index entry."""
        stock = StockIndex(**data.model_dump())
        await stock.insert()
        return stock
    
    @staticmethod
    async def update(id: str, data: StockIndexUpdate) -> StockIndex | None:
        """Update an existing stock index entry."""
        stock = await StockIndexService.get_by_id(id)
        if stock is None:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        update_data["updatedAt"] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(stock, key, value)
        
        await stock.save()
        return stock
    
    @staticmethod
    async def delete(id: str) -> bool:
        """Delete a stock index entry by ID."""
        stock = await StockIndexService.get_by_id(id)
        if stock is None:
            return False
        
        await stock.delete()
        return True
    
    @staticmethod
    async def count(
        isin: str | None = None,
        ticker: str | None = None,
        exchange_code: str | None = None,
        security_type: str | None = None,
        name: str | None = None,
    ) -> int:
        """Get the total count of stocks with optional filtering."""
        query = {}
        
        if isin:
            query["isin"] = isin
        if ticker:
            query["ticker"] = {"$regex": f"^{ticker}", "$options": "i"}
        if exchange_code:
            query["exchangeCode"] = exchange_code
        if security_type:
            query["securityType"] = security_type
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        
        return await StockIndex.find(query).count()
    
    @staticmethod
    async def get_by_exchange(
        exchange_code: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[StockIndex]:
        """Get all stocks for a specific exchange."""
        return await StockIndex.find(
            {"exchangeCode": exchange_code}
        ).skip(skip).limit(limit).sort("name").to_list()
