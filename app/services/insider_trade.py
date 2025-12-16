"""Service for InsiderTrade CRUD operations."""

from datetime import datetime
from math import ceil

from beanie import PydanticObjectId

from app.models.insider_trade import InsiderTrade
from app.schemas.insider_trade import InsiderTradeCreate, InsiderTradeUpdate


class InsiderTradeService:
    """Service class for InsiderTrade operations."""
    
    # Transaction methods to exclude when filtering for real trades only
    NON_TRADE_METHODS = [
        "award_or_grant",
        "gift",
        "tax_withholding_or_exercise_cost",
        "conversion",
        "exercise",
        "expiration",
        "discretionary_transaction",
    ]
    
    @staticmethod
    async def get_all(
        skip: int = 0,
        limit: int = 100,
        isin: str | None = None,
        jurisdiction: str | None = None,
        transaction_type: str | None = None,
        source: str | None = None,
        company_name: str | None = None,
        insider_name: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
        exclude_non_trades: bool = False,
    ) -> list[InsiderTrade]:
        """Get all insider trades with pagination and filtering."""
        query = {}
        
        if isin:
            query["isin"] = isin
        if jurisdiction:
            query["jurisdiction"] = jurisdiction
        if transaction_type:
            query["transactionType"] = transaction_type
        if source:
            query["source"] = source
        if company_name:
            query["companyName"] = {"$regex": company_name, "$options": "i"}
        if insider_name:
            query["insiderName"] = {"$regex": insider_name, "$options": "i"}
        if from_date:
            query["transactionDate"] = query.get("transactionDate", {})
            query["transactionDate"]["$gte"] = from_date
        if to_date:
            query["transactionDate"] = query.get("transactionDate", {})
            query["transactionDate"]["$lte"] = to_date
        if min_amount is not None:
            query["totalAmount"] = query.get("totalAmount", {})
            query["totalAmount"]["$gte"] = min_amount
        if max_amount is not None:
            query["totalAmount"] = query.get("totalAmount", {})
            query["totalAmount"]["$lte"] = max_amount
        if exclude_non_trades:
            query["transactionMethod"] = {"$nin": InsiderTradeService.NON_TRADE_METHODS}
        
        return await InsiderTrade.find(query).skip(skip).limit(limit).sort("-transactionDate").to_list()
    
    @staticmethod
    async def get_by_id(id: str) -> InsiderTrade | None:
        """Get an insider trade by ID."""
        try:
            return await InsiderTrade.get(PydanticObjectId(id))
        except Exception:
            return None
    
    @staticmethod
    async def get_by_isin(
        isin: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[InsiderTrade]:
        """Get all insider trades for a specific ISIN."""
        return await InsiderTrade.find({"isin": isin}).skip(skip).limit(limit).sort("-transactionDate").to_list()
    
    @staticmethod
    async def get_by_company(
        company_name: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[InsiderTrade]:
        """Get all insider trades for a specific company (partial match)."""
        return await InsiderTrade.find(
            {"companyName": {"$regex": company_name, "$options": "i"}}
        ).skip(skip).limit(limit).sort("-transactionDate").to_list()
    
    @staticmethod
    async def create(data: InsiderTradeCreate) -> InsiderTrade:
        """Create a new insider trade."""
        trade = InsiderTrade(**data.model_dump(by_alias=True))
        await trade.insert()
        return trade
    
    @staticmethod
    async def update(id: str, data: InsiderTradeUpdate) -> InsiderTrade | None:
        """Update an existing insider trade."""
        trade = await InsiderTradeService.get_by_id(id)
        if trade is None:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        update_data["updatedAt"] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(trade, key, value)
        
        await trade.save()
        return trade
    
    @staticmethod
    async def delete(id: str) -> bool:
        """Delete an insider trade by ID."""
        trade = await InsiderTradeService.get_by_id(id)
        if trade is None:
            return False
        
        await trade.delete()
        return True
    
    @staticmethod
    async def count(
        isin: str | None = None,
        jurisdiction: str | None = None,
        transaction_type: str | None = None,
        source: str | None = None,
        company_name: str | None = None,
        insider_name: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
        exclude_non_trades: bool = False,
    ) -> int:
        """Get the total count of insider trades with optional filtering."""
        query = {}
        
        if isin:
            query["isin"] = isin
        if jurisdiction:
            query["jurisdiction"] = jurisdiction
        if transaction_type:
            query["transactionType"] = transaction_type
        if source:
            query["source"] = source
        if company_name:
            query["companyName"] = {"$regex": company_name, "$options": "i"}
        if insider_name:
            query["insiderName"] = {"$regex": insider_name, "$options": "i"}
        if from_date:
            query["transactionDate"] = query.get("transactionDate", {})
            query["transactionDate"]["$gte"] = from_date
        if to_date:
            query["transactionDate"] = query.get("transactionDate", {})
            query["transactionDate"]["$lte"] = to_date
        if min_amount is not None:
            query["totalAmount"] = query.get("totalAmount", {})
            query["totalAmount"]["$gte"] = min_amount
        if max_amount is not None:
            query["totalAmount"] = query.get("totalAmount", {})
            query["totalAmount"]["$lte"] = max_amount
        if exclude_non_trades:
            query["transactionMethod"] = {"$nin": InsiderTradeService.NON_TRADE_METHODS}
        
        return await InsiderTrade.find(query).count()
    
    @staticmethod
    async def get_recent_by_jurisdiction(
        jurisdiction: str,
        limit: int = 10,
    ) -> list[InsiderTrade]:
        """Get recent insider trades for a specific jurisdiction."""
        return await InsiderTrade.find(
            {"jurisdiction": jurisdiction}
        ).limit(limit).sort("-transactionDate").to_list()
    
    @staticmethod
    async def get_aggregated_stats(
        isin: str | None = None,
        jurisdiction: str | None = None,
        days: int = 30,
    ) -> dict:
        """Get aggregated statistics for insider trades."""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = {"transactionDate": {"$gte": cutoff_date}}
        
        if isin:
            query["isin"] = isin
        if jurisdiction:
            query["jurisdiction"] = jurisdiction
        
        trades = await InsiderTrade.find(query).to_list()
        
        buy_count = sum(1 for t in trades if t.transactionType == "BUY")
        sell_count = sum(1 for t in trades if t.transactionType == "SELL")
        
        total_buy_amount = sum(
            float(t.totalAmount) if t.totalAmount and t.transactionType == "BUY" else 0
            for t in trades
        )
        total_sell_amount = sum(
            float(t.totalAmount) if t.totalAmount and t.transactionType == "SELL" else 0
            for t in trades
        )
        
        return {
            "period_days": days,
            "total_trades": len(trades),
            "buy_count": buy_count,
            "sell_count": sell_count,
            "total_buy_amount": total_buy_amount,
            "total_sell_amount": total_sell_amount,
            "net_amount": total_buy_amount - total_sell_amount,
        }
