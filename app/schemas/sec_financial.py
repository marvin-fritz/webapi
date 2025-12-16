"""Pydantic schemas for SEC Financials."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class SECFinancialBase(BaseModel):
    """Base schema for SEC Financial data."""
    
    # Company identifiers
    cik: int  # SEC Central Index Key
    ticker: str | None = None
    companyName: str | None = None
    
    # Filing information
    accessionNumber: str | None = None
    filingDate: datetime | None = None
    reportDate: datetime | None = None
    fiscalYear: int | None = None
    fiscalPeriod: str | None = None  # Q1, Q2, Q3, Q4, FY
    form: str | None = None  # 10-K, 10-Q, etc.
    
    # Financial metrics - Income Statement
    revenue: float | None = None
    costOfRevenue: float | None = None
    grossProfit: float | None = None
    operatingExpenses: float | None = None
    operatingIncome: float | None = None
    netIncome: float | None = None
    eps: float | None = None
    epsDiluted: float | None = None
    
    # Financial metrics - Balance Sheet
    totalAssets: float | None = None
    totalLiabilities: float | None = None
    totalEquity: float | None = None
    cash: float | None = None
    totalDebt: float | None = None
    currentAssets: float | None = None
    currentLiabilities: float | None = None
    
    # Financial metrics - Cash Flow
    operatingCashFlow: float | None = None
    investingCashFlow: float | None = None
    financingCashFlow: float | None = None
    freeCashFlow: float | None = None
    capitalExpenditures: float | None = None
    
    # Ratios and metrics
    profitMargin: float | None = None
    returnOnAssets: float | None = None
    returnOnEquity: float | None = None
    debtToEquity: float | None = None
    currentRatio: float | None = None
    
    # Currency
    currency: str = "USD"


class SECFinancialCreate(SECFinancialBase):
    """Schema for creating a SEC Financial entry."""
    
    rawData: dict[str, Any] | None = None


class SECFinancialUpdate(BaseModel):
    """Schema for updating a SEC Financial entry. All fields optional."""
    
    ticker: str | None = None
    companyName: str | None = None
    accessionNumber: str | None = None
    filingDate: datetime | None = None
    reportDate: datetime | None = None
    fiscalYear: int | None = None
    fiscalPeriod: str | None = None
    form: str | None = None
    revenue: float | None = None
    costOfRevenue: float | None = None
    grossProfit: float | None = None
    operatingExpenses: float | None = None
    operatingIncome: float | None = None
    netIncome: float | None = None
    eps: float | None = None
    epsDiluted: float | None = None
    totalAssets: float | None = None
    totalLiabilities: float | None = None
    totalEquity: float | None = None
    cash: float | None = None
    totalDebt: float | None = None
    currentAssets: float | None = None
    currentLiabilities: float | None = None
    operatingCashFlow: float | None = None
    investingCashFlow: float | None = None
    financingCashFlow: float | None = None
    freeCashFlow: float | None = None
    capitalExpenditures: float | None = None
    profitMargin: float | None = None
    returnOnAssets: float | None = None
    returnOnEquity: float | None = None
    debtToEquity: float | None = None
    currentRatio: float | None = None
    currency: str | None = None
    rawData: dict[str, Any] | None = None


class SECFinancialResponse(SECFinancialBase):
    """Schema for SEC Financial response."""
    
    id: str = Field(..., description="MongoDB ObjectId as string")
    rawData: dict[str, Any] | None = None
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True


class SECFinancialListResponse(BaseModel):
    """Paginated response for SEC financials."""
    
    items: list[SECFinancialResponse]
    total: int
    page: int
    pageSize: int
    pages: int


class SECFinancialFilters(BaseModel):
    """Filter options for SEC financials query."""
    
    cik: int | None = None
    ticker: str | None = None
    companyName: str | None = None  # Partial match search
    fiscalYear: int | None = None
    fiscalPeriod: str | None = None
    form: str | None = None
    fromDate: datetime | None = None
    toDate: datetime | None = None
