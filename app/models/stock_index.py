"""Beanie Document model for StockIndex collection."""

from datetime import datetime, timezone

from beanie import Document
from pydantic import BaseModel, Field


class StockIdentifiers(BaseModel):
    """Embedded document for stock identifiers."""
    
    isin: str | None = None
    figi: str | None = None
    compositeFigi: str | None = None
    cik: int | None = None


class InsiderTradingScan(BaseModel):
    """Embedded document for insider trading scan metadata."""
    
    latestScan: datetime | None = None
    lastAccession: str | None = None


class QuarterlyFinancialsScan(BaseModel):
    """Embedded document for quarterly financials scan metadata."""
    
    latestScan: datetime | None = None


class StockScans(BaseModel):
    """Embedded document for scan metadata."""
    
    insiderTrading: InsiderTradingScan | None = None
    quarterlyFinancials: QuarterlyFinancialsScan | None = None


class StockIndex(Document):
    """Document model for the stockIndex collection."""
    
    name: str
    identifiers: StockIdentifiers
    ticker: str
    exchangeCode: str
    securityType: str  # Common Stock, ADR, GDR, Preference
    marketSector: str  # Equity
    scans: StockScans | None = None
    isin: str | None = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "stockIndex"  # MongoDB collection name
        use_state_management = True
