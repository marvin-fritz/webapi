"""Beanie Document model for SEC Financials collection."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from beanie import Document
from bson import Decimal128
from pydantic import Field, field_validator


def decimal128_to_decimal(v: Any) -> Decimal | None:
    """Convert Decimal128 to Decimal."""
    if v is None:
        return None
    if isinstance(v, Decimal128):
        return Decimal(str(v))
    if isinstance(v, (int, float, str, Decimal)):
        return Decimal(str(v))
    return v


class SECFinancial(Document):
    """Document model for the sec_financials collection.
    
    Contains financial data for US companies from SEC filings.
    """
    
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
    revenue: Decimal | None = None
    costOfRevenue: Decimal | None = None
    grossProfit: Decimal | None = None
    operatingExpenses: Decimal | None = None
    operatingIncome: Decimal | None = None
    netIncome: Decimal | None = None
    eps: Decimal | None = None  # Earnings per share
    epsDiluted: Decimal | None = None
    
    # Financial metrics - Balance Sheet
    totalAssets: Decimal | None = None
    totalLiabilities: Decimal | None = None
    totalEquity: Decimal | None = None
    cash: Decimal | None = None
    totalDebt: Decimal | None = None
    currentAssets: Decimal | None = None
    currentLiabilities: Decimal | None = None
    
    # Financial metrics - Cash Flow
    operatingCashFlow: Decimal | None = None
    investingCashFlow: Decimal | None = None
    financingCashFlow: Decimal | None = None
    freeCashFlow: Decimal | None = None
    capitalExpenditures: Decimal | None = None
    
    # Ratios and metrics
    profitMargin: Decimal | None = None
    returnOnAssets: Decimal | None = None
    returnOnEquity: Decimal | None = None
    debtToEquity: Decimal | None = None
    currentRatio: Decimal | None = None
    
    # Currency
    currency: str = "USD"
    
    # Metadata
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Additional raw data from SEC
    rawData: dict[str, Any] | None = None
    
    # Validators to convert Decimal128 from MongoDB to Decimal
    @field_validator(
        "revenue", "costOfRevenue", "grossProfit", "operatingExpenses", "operatingIncome",
        "netIncome", "eps", "epsDiluted", "totalAssets", "totalLiabilities", "totalEquity",
        "cash", "totalDebt", "currentAssets", "currentLiabilities", "operatingCashFlow",
        "investingCashFlow", "financingCashFlow", "freeCashFlow", "capitalExpenditures",
        "profitMargin", "returnOnAssets", "returnOnEquity", "debtToEquity", "currentRatio",
        mode="before"
    )
    @classmethod
    def convert_decimal128(cls, v: Any) -> Decimal | None:
        return decimal128_to_decimal(v)
    
    class Settings:
        name = "sec_financials"  # MongoDB collection name
        use_state_management = True
        bson_encoders = {
            Decimal: lambda v: Decimal128(str(v)) if v is not None else None
        }
