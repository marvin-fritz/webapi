"""REST API endpoints for SEC Financials."""

from datetime import datetime
from math import ceil

from fastapi import APIRouter, HTTPException, Query

from app.schemas.sec_financial import (
    SECFinancialCreate,
    SECFinancialListResponse,
    SECFinancialResponse,
    SECFinancialUpdate,
)
from app.services.sec_financial import SECFinancialService

router = APIRouter()


def _decimal_to_float(value) -> float | None:
    """Convert Decimal to float, handling None values."""
    if value is None:
        return None
    return float(value)


def _financial_to_response(financial) -> SECFinancialResponse:
    """Convert SECFinancial document to response schema."""
    return SECFinancialResponse(
        id=str(financial.id),
        cik=financial.cik,
        ticker=financial.ticker,
        companyName=financial.companyName,
        accessionNumber=financial.accessionNumber,
        filingDate=financial.filingDate,
        reportDate=financial.reportDate,
        fiscalYear=financial.fiscalYear,
        fiscalPeriod=financial.fiscalPeriod,
        form=financial.form,
        revenue=_decimal_to_float(financial.revenue),
        costOfRevenue=_decimal_to_float(financial.costOfRevenue),
        grossProfit=_decimal_to_float(financial.grossProfit),
        operatingExpenses=_decimal_to_float(financial.operatingExpenses),
        operatingIncome=_decimal_to_float(financial.operatingIncome),
        netIncome=_decimal_to_float(financial.netIncome),
        eps=_decimal_to_float(financial.eps),
        epsDiluted=_decimal_to_float(financial.epsDiluted),
        totalAssets=_decimal_to_float(financial.totalAssets),
        totalLiabilities=_decimal_to_float(financial.totalLiabilities),
        totalEquity=_decimal_to_float(financial.totalEquity),
        cash=_decimal_to_float(financial.cash),
        totalDebt=_decimal_to_float(financial.totalDebt),
        currentAssets=_decimal_to_float(financial.currentAssets),
        currentLiabilities=_decimal_to_float(financial.currentLiabilities),
        operatingCashFlow=_decimal_to_float(financial.operatingCashFlow),
        investingCashFlow=_decimal_to_float(financial.investingCashFlow),
        financingCashFlow=_decimal_to_float(financial.financingCashFlow),
        freeCashFlow=_decimal_to_float(financial.freeCashFlow),
        capitalExpenditures=_decimal_to_float(financial.capitalExpenditures),
        profitMargin=_decimal_to_float(financial.profitMargin),
        returnOnAssets=_decimal_to_float(financial.returnOnAssets),
        returnOnEquity=_decimal_to_float(financial.returnOnEquity),
        debtToEquity=_decimal_to_float(financial.debtToEquity),
        currentRatio=_decimal_to_float(financial.currentRatio),
        currency=financial.currency,
        rawData=financial.rawData,
        createdAt=financial.createdAt,
        updatedAt=financial.updatedAt,
    )


@router.get("", response_model=SECFinancialListResponse)
async def get_all_sec_financials(
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(50, ge=1, le=500, description="Items per page"),
    cik: int | None = Query(None, description="Filter by CIK (SEC Central Index Key)"),
    ticker: str | None = Query(None, description="Filter by ticker symbol"),
    companyName: str | None = Query(None, description="Filter by company name (partial match)"),
    fiscalYear: int | None = Query(None, description="Filter by fiscal year"),
    fiscalPeriod: str | None = Query(None, description="Filter by fiscal period (Q1, Q2, Q3, Q4, FY)"),
    form: str | None = Query(None, description="Filter by form type (10-K, 10-Q)"),
    fromDate: datetime | None = Query(None, description="Filter filings from this date"),
    toDate: datetime | None = Query(None, description="Filter filings up to this date"),
) -> SECFinancialListResponse:
    """Get all SEC financials with pagination and filtering.
    
    Note: This endpoint only contains financial data for US companies filed with the SEC.
    """
    skip = (page - 1) * pageSize
    
    financials = await SECFinancialService.get_all(
        skip=skip,
        limit=pageSize,
        cik=cik,
        ticker=ticker,
        company_name=companyName,
        fiscal_year=fiscalYear,
        fiscal_period=fiscalPeriod,
        form=form,
        from_date=fromDate,
        to_date=toDate,
    )
    
    total = await SECFinancialService.count(
        cik=cik,
        ticker=ticker,
        company_name=companyName,
        fiscal_year=fiscalYear,
        fiscal_period=fiscalPeriod,
        form=form,
        from_date=fromDate,
        to_date=toDate,
    )
    
    return SECFinancialListResponse(
        items=[_financial_to_response(f) for f in financials],
        total=total,
        page=page,
        pageSize=pageSize,
        pages=ceil(total / pageSize) if total > 0 else 0,
    )


@router.get("/cik/{cik}", response_model=SECFinancialListResponse)
async def get_sec_financials_by_cik(
    cik: int,
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(50, ge=1, le=500, description="Items per page"),
    fiscalYear: int | None = Query(None, description="Filter by fiscal year"),
    fiscalPeriod: str | None = Query(None, description="Filter by fiscal period (Q1, Q2, Q3, Q4, FY)"),
) -> SECFinancialListResponse:
    """Get SEC financials by CIK (SEC Central Index Key)."""
    skip = (page - 1) * pageSize
    
    financials = await SECFinancialService.get_by_cik(
        cik=cik,
        skip=skip,
        limit=pageSize,
        fiscal_year=fiscalYear,
        fiscal_period=fiscalPeriod,
    )
    
    total = await SECFinancialService.count(
        cik=cik,
        fiscal_year=fiscalYear,
        fiscal_period=fiscalPeriod,
    )
    
    return SECFinancialListResponse(
        items=[_financial_to_response(f) for f in financials],
        total=total,
        page=page,
        pageSize=pageSize,
        pages=ceil(total / pageSize) if total > 0 else 0,
    )


@router.get("/ticker/{ticker}", response_model=SECFinancialListResponse)
async def get_sec_financials_by_ticker(
    ticker: str,
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(50, ge=1, le=500, description="Items per page"),
    fiscalYear: int | None = Query(None, description="Filter by fiscal year"),
    fiscalPeriod: str | None = Query(None, description="Filter by fiscal period (Q1, Q2, Q3, Q4, FY)"),
) -> SECFinancialListResponse:
    """Get SEC financials by ticker symbol."""
    skip = (page - 1) * pageSize
    
    financials = await SECFinancialService.get_by_ticker(
        ticker=ticker,
        skip=skip,
        limit=pageSize,
        fiscal_year=fiscalYear,
        fiscal_period=fiscalPeriod,
    )
    
    total = await SECFinancialService.count(
        ticker=ticker,
        fiscal_year=fiscalYear,
        fiscal_period=fiscalPeriod,
    )
    
    return SECFinancialListResponse(
        items=[_financial_to_response(f) for f in financials],
        total=total,
        page=page,
        pageSize=pageSize,
        pages=ceil(total / pageSize) if total > 0 else 0,
    )


@router.get("/ticker/{ticker}/latest", response_model=SECFinancialResponse)
async def get_latest_sec_financial_by_ticker(
    ticker: str,
    form: str | None = Query(None, description="Filter by form type (10-K, 10-Q)"),
) -> SECFinancialResponse:
    """Get the latest SEC financial data for a specific ticker."""
    financial = await SECFinancialService.get_latest_by_ticker(ticker=ticker, form=form)
    
    if not financial:
        raise HTTPException(
            status_code=404,
            detail=f"No SEC financial data found for ticker {ticker.upper()}",
        )
    
    return _financial_to_response(financial)


@router.get("/cik/{cik}/latest", response_model=SECFinancialResponse)
async def get_latest_sec_financial_by_cik(
    cik: int,
    form: str | None = Query(None, description="Filter by form type (10-K, 10-Q)"),
) -> SECFinancialResponse:
    """Get the latest SEC financial data for a specific CIK."""
    financial = await SECFinancialService.get_latest_by_cik(cik=cik, form=form)
    
    if not financial:
        raise HTTPException(
            status_code=404,
            detail=f"No SEC financial data found for CIK {cik}",
        )
    
    return _financial_to_response(financial)


@router.get("/{id}", response_model=SECFinancialResponse)
async def get_sec_financial_by_id(id: str) -> SECFinancialResponse:
    """Get SEC financial data by ID."""
    financial = await SECFinancialService.get_by_id(id)
    
    if not financial:
        raise HTTPException(
            status_code=404,
            detail=f"SEC financial data with ID {id} not found",
        )
    
    return _financial_to_response(financial)


@router.post("", response_model=SECFinancialResponse, status_code=201)
async def create_sec_financial(data: SECFinancialCreate) -> SECFinancialResponse:
    """Create a new SEC financial entry."""
    financial = await SECFinancialService.create(data)
    return _financial_to_response(financial)


@router.patch("/{id}", response_model=SECFinancialResponse)
async def update_sec_financial(id: str, data: SECFinancialUpdate) -> SECFinancialResponse:
    """Update an SEC financial entry."""
    financial = await SECFinancialService.update(id, data)
    
    if not financial:
        raise HTTPException(
            status_code=404,
            detail=f"SEC financial data with ID {id} not found",
        )
    
    return _financial_to_response(financial)


@router.delete("/{id}", status_code=204)
async def delete_sec_financial(id: str) -> None:
    """Delete an SEC financial entry."""
    success = await SECFinancialService.delete(id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"SEC financial data with ID {id} not found",
        )
