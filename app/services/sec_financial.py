"""Service for SEC Financials CRUD operations."""

from datetime import datetime
from math import ceil

from beanie import PydanticObjectId

from app.models.sec_financial import SECFinancial
from app.schemas.sec_financial import SECFinancialCreate, SECFinancialUpdate


class SECFinancialService:
    """Service class for SEC Financial operations."""
    
    @staticmethod
    async def get_all(
        skip: int = 0,
        limit: int = 100,
        cik: int | None = None,
        ticker: str | None = None,
        company_name: str | None = None,
        fiscal_year: int | None = None,
        fiscal_period: str | None = None,
        form: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[SECFinancial]:
        """Get all SEC financials with pagination and filtering."""
        query = {}
        
        if cik:
            query["cik"] = cik
        if ticker:
            query["ticker"] = ticker.upper()
        if company_name:
            query["companyName"] = {"$regex": company_name, "$options": "i"}
        if fiscal_year:
            query["fiscalYear"] = fiscal_year
        if fiscal_period:
            query["fiscalPeriod"] = fiscal_period
        if form:
            query["form"] = form
        if from_date:
            query["filingDate"] = query.get("filingDate", {})
            query["filingDate"]["$gte"] = from_date
        if to_date:
            query["filingDate"] = query.get("filingDate", {})
            query["filingDate"]["$lte"] = to_date
        
        return await SECFinancial.find(query).skip(skip).limit(limit).sort("-filingDate").to_list()
    
    @staticmethod
    async def get_by_id(id: str) -> SECFinancial | None:
        """Get SEC financial data by ID."""
        try:
            return await SECFinancial.get(PydanticObjectId(id))
        except Exception:
            return None
    
    @staticmethod
    async def get_by_cik(
        cik: int,
        skip: int = 0,
        limit: int = 100,
        fiscal_year: int | None = None,
        fiscal_period: str | None = None,
    ) -> list[SECFinancial]:
        """Get all SEC financials for a specific CIK (company)."""
        query = {"cik": cik}
        if fiscal_year:
            query["fiscalYear"] = fiscal_year
        if fiscal_period:
            query["fiscalPeriod"] = fiscal_period
        
        return await SECFinancial.find(query).skip(skip).limit(limit).sort("-filingDate").to_list()
    
    @staticmethod
    async def get_by_ticker(
        ticker: str,
        skip: int = 0,
        limit: int = 100,
        fiscal_year: int | None = None,
        fiscal_period: str | None = None,
    ) -> list[SECFinancial]:
        """Get all SEC financials for a specific ticker."""
        query = {"ticker": ticker.upper()}
        if fiscal_year:
            query["fiscalYear"] = fiscal_year
        if fiscal_period:
            query["fiscalPeriod"] = fiscal_period
        
        return await SECFinancial.find(query).skip(skip).limit(limit).sort("-filingDate").to_list()
    
    @staticmethod
    async def get_latest_by_ticker(
        ticker: str,
        form: str | None = None,
    ) -> SECFinancial | None:
        """Get the latest SEC financial data for a specific ticker."""
        query = {"ticker": ticker.upper()}
        if form:
            query["form"] = form
        
        results = await SECFinancial.find(query).sort("-filingDate").limit(1).to_list()
        return results[0] if results else None
    
    @staticmethod
    async def get_latest_by_cik(
        cik: int,
        form: str | None = None,
    ) -> SECFinancial | None:
        """Get the latest SEC financial data for a specific CIK."""
        query = {"cik": cik}
        if form:
            query["form"] = form
        
        results = await SECFinancial.find(query).sort("-filingDate").limit(1).to_list()
        return results[0] if results else None
    
    @staticmethod
    async def count(
        cik: int | None = None,
        ticker: str | None = None,
        company_name: str | None = None,
        fiscal_year: int | None = None,
        fiscal_period: str | None = None,
        form: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> int:
        """Count SEC financials with optional filters."""
        query = {}
        
        if cik:
            query["cik"] = cik
        if ticker:
            query["ticker"] = ticker.upper()
        if company_name:
            query["companyName"] = {"$regex": company_name, "$options": "i"}
        if fiscal_year:
            query["fiscalYear"] = fiscal_year
        if fiscal_period:
            query["fiscalPeriod"] = fiscal_period
        if form:
            query["form"] = form
        if from_date:
            query["filingDate"] = query.get("filingDate", {})
            query["filingDate"]["$gte"] = from_date
        if to_date:
            query["filingDate"] = query.get("filingDate", {})
            query["filingDate"]["$lte"] = to_date
        
        return await SECFinancial.find(query).count()
    
    @staticmethod
    async def create(data: SECFinancialCreate) -> SECFinancial:
        """Create a new SEC financial entry."""
        financial = SECFinancial(**data.model_dump())
        await financial.insert()
        return financial
    
    @staticmethod
    async def update(id: str, data: SECFinancialUpdate) -> SECFinancial | None:
        """Update an SEC financial entry."""
        financial = await SECFinancialService.get_by_id(id)
        if not financial:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await financial.set(update_data)
        
        return financial
    
    @staticmethod
    async def delete(id: str) -> bool:
        """Delete an SEC financial entry."""
        financial = await SECFinancialService.get_by_id(id)
        if not financial:
            return False
        
        await financial.delete()
        return True
