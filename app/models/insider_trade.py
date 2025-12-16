"""Beanie Document model for InsiderTrade collection."""

from datetime import datetime, timezone
from decimal import Decimal

from beanie import Document
from pydantic import BaseModel, Field


class InsiderTradeLookup(BaseModel):
    """Embedded document for lookup metadata."""
    
    isin: str | None = None
    source: str | None = None
    jurisdiction: str | None = None
    transactionDate: datetime | None = None


class InsiderTradeSourceMetadata(BaseModel):
    """Embedded document for source-specific metadata."""
    
    # Common fields
    venue: str | None = None
    activationDate: datetime | None = None
    
    # BaFin specific
    bafinId: str | None = None
    
    # SER (Swiss) specific
    notificationSubmitterId: str | None = None
    obligorFunctionCode: str | None = None
    securityTypeCode: str | None = None
    buySellIndicator: str | None = None
    swxListed: str | None = None
    sdxListed: str | None = None
    obligorRelatedPartyInd: str | None = None
    
    class Config:
        extra = "allow"


class InsiderTrade(Document):
    """Document model for the insiderTrades collection."""
    
    uid: str
    lookup: InsiderTradeLookup | None = Field(None, alias="_lookup")
    companyName: str
    currency: str
    filingDate: datetime
    filingId: str
    insiderName: str
    insiderRole: str | None = None
    isDirector: bool = False
    isOfficer: bool = False
    isin: str
    jurisdiction: str
    ownershipType: str  # DIRECT, INDIRECT
    pricePerShare: Decimal | None = None
    securityTitle: str
    securityType: str  # EQUITY, OPTION, etc.
    shares: Decimal | None = None
    source: str  # ser, bafin, sec, etc.
    sourceMetadata: InsiderTradeSourceMetadata | None = None
    totalAmount: Decimal | None = None
    totalAmountSigned: Decimal | None = None
    transactionDate: datetime
    transactionMethod: str  # open_market_purchase, open_market_sale, etc.
    transactionType: str  # BUY, SELL
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "insiderTrades"  # MongoDB collection name
        use_state_management = True
        bson_encoders = {
            Decimal: lambda v: str(v) if v is not None else None
        }
