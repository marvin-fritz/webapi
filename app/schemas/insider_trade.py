"""Pydantic schemas for InsiderTrade."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class InsiderTradeLookup(BaseModel):
    """Lookup metadata for insider trade."""
    
    isin: str | None = None
    source: str | None = None
    jurisdiction: str | None = None
    transactionDate: datetime | None = None


class InsiderTradeSourceMetadata(BaseModel):
    """Source-specific metadata for insider trade."""
    
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
        extra = "allow"  # Allow additional fields from different sources


class InsiderTradeBase(BaseModel):
    """Base schema for InsiderTrade."""
    
    uid: str
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
    totalAmount: Decimal | None = None
    totalAmountSigned: Decimal | None = None
    transactionDate: datetime
    transactionMethod: str  # open_market_purchase, open_market_sale, etc.
    transactionType: str  # BUY, SELL


class InsiderTradeCreate(InsiderTradeBase):
    """Schema for creating an InsiderTrade."""
    
    lookup: InsiderTradeLookup | None = Field(None, alias="_lookup")
    sourceMetadata: InsiderTradeSourceMetadata | None = None


class InsiderTradeUpdate(BaseModel):
    """Schema for updating an InsiderTrade. All fields optional."""
    
    uid: str | None = None
    companyName: str | None = None
    currency: str | None = None
    filingDate: datetime | None = None
    filingId: str | None = None
    insiderName: str | None = None
    insiderRole: str | None = None
    isDirector: bool | None = None
    isOfficer: bool | None = None
    isin: str | None = None
    jurisdiction: str | None = None
    ownershipType: str | None = None
    pricePerShare: Decimal | None = None
    securityTitle: str | None = None
    securityType: str | None = None
    shares: Decimal | None = None
    source: str | None = None
    totalAmount: Decimal | None = None
    totalAmountSigned: Decimal | None = None
    transactionDate: datetime | None = None
    transactionMethod: str | None = None
    transactionType: str | None = None
    sourceMetadata: InsiderTradeSourceMetadata | None = None


class InsiderTradeResponse(BaseModel):
    """Schema for InsiderTrade response."""
    
    id: str = Field(..., description="MongoDB ObjectId as string")
    uid: str
    companyName: str
    currency: str
    filingDate: datetime
    filingId: str
    insiderName: str
    insiderRole: str | None = None
    isDirector: bool
    isOfficer: bool
    isin: str
    jurisdiction: str
    ownershipType: str
    pricePerShare: float | None = None
    securityTitle: str
    securityType: str
    shares: float | None = None
    source: str
    sourceMetadata: InsiderTradeSourceMetadata | None = None
    totalAmount: float | None = None
    totalAmountSigned: float | None = None
    transactionDate: datetime
    transactionMethod: str
    transactionType: str
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True


class InsiderTradeListResponse(BaseModel):
    """Paginated response for insider trades."""
    
    items: list[InsiderTradeResponse]
    total: int
    page: int
    pageSize: int
    pages: int


class InsiderTradeFilters(BaseModel):
    """Filter options for insider trades query."""
    
    isin: str | None = None
    jurisdiction: str | None = None
    transactionType: str | None = None  # BUY, SELL
    source: str | None = None  # ser, bafin, sec
    companyName: str | None = None
    insiderName: str | None = None
    fromDate: datetime | None = None
    toDate: datetime | None = None
    minAmount: float | None = None
    maxAmount: float | None = None
