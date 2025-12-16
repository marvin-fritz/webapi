"""Pydantic schemas for StockIndex."""

from datetime import datetime

from pydantic import BaseModel, Field


class StockIdentifiers(BaseModel):
    """Identifiers for a stock."""
    
    isin: str | None = None
    figi: str | None = None
    compositeFigi: str | None = None
    cik: int | None = None


class InsiderTradingScan(BaseModel):
    """Insider trading scan metadata."""
    
    latestScan: datetime | None = None
    lastAccession: str | None = None


class QuarterlyFinancialsScan(BaseModel):
    """Quarterly financials scan metadata."""
    
    latestScan: datetime | None = None


class StockScans(BaseModel):
    """Scan metadata for a stock."""
    
    insiderTrading: InsiderTradingScan | None = None
    quarterlyFinancials: QuarterlyFinancialsScan | None = None


class StockIndexBase(BaseModel):
    """Base schema for StockIndex."""
    
    name: str
    identifiers: StockIdentifiers
    ticker: str
    exchangeCode: str
    securityType: str  # Common Stock, ADR, GDR, Preference
    marketSector: str  # Equity
    isin: str | None = None


class StockIndexCreate(StockIndexBase):
    """Schema for creating a StockIndex entry."""
    
    scans: StockScans | None = None


class StockIndexUpdate(BaseModel):
    """Schema for updating a StockIndex entry. All fields optional."""
    
    name: str | None = None
    identifiers: StockIdentifiers | None = None
    ticker: str | None = None
    exchangeCode: str | None = None
    securityType: str | None = None
    marketSector: str | None = None
    isin: str | None = None
    scans: StockScans | None = None


class StockIndexResponse(StockIndexBase):
    """Schema for StockIndex response."""
    
    id: str = Field(..., description="MongoDB ObjectId as string")
    scans: StockScans | None = None
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True


class StockIndexListResponse(BaseModel):
    """Paginated response for stock index."""
    
    items: list[StockIndexResponse]
    total: int
    page: int
    pageSize: int
    pages: int


class StockIndexFilters(BaseModel):
    """Filter options for stock index query."""
    
    isin: str | None = None
    ticker: str | None = None
    exchangeCode: str | None = None
    securityType: str | None = None
    name: str | None = None  # Partial match search
