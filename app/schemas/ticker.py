"""Pydantic schemas for Ticker (Insider Trade Signals)."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TickerSignal(str, Enum):
    """Signal types for insider trading patterns."""
    
    CLUSTER_BUYING = "CLUSTER_BUYING"  # Multiple insiders buying
    HIGH_VOLUME = "HIGH_VOLUME"  # High transaction volume (>100k)
    PURE_BUYING = "PURE_BUYING"  # Only buys, no sells
    DOMINANT_BUYING = "DOMINANT_BUYING"  # Buy volume > 2x sell volume


class TickerItem(BaseModel):
    """Single ticker with insider trading signals."""
    
    uid: str = Field(..., description="Unique identifier for frontend keys")
    isin: str = Field(..., description="ISIN of the stock")
    companyName: str = Field(..., description="Company name")
    currency: str | None = Field(None, description="Transaction currency")
    lastTransactionDate: datetime | None = Field(None, description="Most recent transaction date")
    
    # Trade counts
    tradeCount: int = Field(0, description="Total number of trades")
    buyCount: int = Field(0, description="Number of buy transactions")
    sellCount: int = Field(0, description="Number of sell transactions")
    
    # Volume metrics
    buyVolume: float = Field(0.0, description="Total buy volume")
    sellVolume: float = Field(0.0, description="Total sell volume")
    netVolume: float = Field(0.0, description="Net volume (buy - sell)")
    
    # Unique insiders
    uniqueBuyersCount: int = Field(0, description="Number of unique buyers")
    uniqueSellersCount: int = Field(0, description="Number of unique sellers")
    buyers: list[str] = Field(default_factory=list, description="List of buyer names")
    sellers: list[str] = Field(default_factory=list, description="List of seller names")
    
    # Analysis
    signals: list[TickerSignal] = Field(default_factory=list, description="Detected trading signals")
    headline: str = Field("", description="Human-readable summary")


class TickerMeta(BaseModel):
    """Metadata for ticker response."""
    
    generatedAt: datetime = Field(..., description="Response generation timestamp")
    windowDays: int = Field(..., description="Analysis window in days")
    minTrades: int = Field(..., description="Minimum trades filter")
    minTotalAmount: float = Field(..., description="Minimum buy volume filter")
    limit: int = Field(..., description="Maximum results")
    count: int = Field(..., description="Actual result count")
    singleIsin: str | None = Field(None, description="Single ISIN filter if applied")


class TickerResponse(BaseModel):
    """Response for ticker endpoint."""
    
    meta: TickerMeta
    items: list[TickerItem]


class TickerSingleNotFoundResponse(BaseModel):
    """Response when no data found for single ISIN."""
    
    data: bool = False
    message: str
