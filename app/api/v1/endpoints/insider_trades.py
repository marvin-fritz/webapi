"""REST API endpoints for InsiderTrade."""

from datetime import datetime
from math import ceil

from fastapi import APIRouter, HTTPException, Query

from app.schemas.insider_trade import (
    InsiderTradeCreate,
    InsiderTradeListResponse,
    InsiderTradeResponse,
    InsiderTradeSourceMetadata,
    InsiderTradeUpdate,
)
from app.services.insider_trade import InsiderTradeService

router = APIRouter()


def _trade_to_response(trade) -> InsiderTradeResponse:
    """Convert InsiderTrade document to response schema."""
    # Convert sourceMetadata from model to schema
    source_metadata = None
    if trade.sourceMetadata:
        source_metadata = InsiderTradeSourceMetadata(
            venue=trade.sourceMetadata.venue,
            activationDate=trade.sourceMetadata.activationDate,
            bafinId=trade.sourceMetadata.bafinId,
            notificationSubmitterId=trade.sourceMetadata.notificationSubmitterId,
            obligorFunctionCode=trade.sourceMetadata.obligorFunctionCode,
            securityTypeCode=trade.sourceMetadata.securityTypeCode,
            buySellIndicator=trade.sourceMetadata.buySellIndicator,
            swxListed=trade.sourceMetadata.swxListed,
            sdxListed=trade.sourceMetadata.sdxListed,
            obligorRelatedPartyInd=trade.sourceMetadata.obligorRelatedPartyInd,
        )
    
    return InsiderTradeResponse(
        id=str(trade.id),
        uid=trade.uid,
        companyName=trade.companyName,
        currency=trade.currency,
        filingDate=trade.filingDate,
        filingId=trade.filingId,
        insiderName=trade.insiderName,
        insiderRole=trade.insiderRole,
        isDirector=trade.isDirector,
        isOfficer=trade.isOfficer,
        isin=trade.isin,
        jurisdiction=trade.jurisdiction,
        ownershipType=trade.ownershipType,
        pricePerShare=float(trade.pricePerShare) if trade.pricePerShare else None,
        securityTitle=trade.securityTitle,
        securityType=trade.securityType,
        shares=float(trade.shares) if trade.shares else None,
        source=trade.source,
        sourceMetadata=source_metadata,
        totalAmount=float(trade.totalAmount) if trade.totalAmount else None,
        totalAmountSigned=float(trade.totalAmountSigned) if trade.totalAmountSigned else None,
        transactionDate=trade.transactionDate,
        transactionMethod=trade.transactionMethod,
        transactionType=trade.transactionType,
        createdAt=trade.createdAt,
        updatedAt=trade.updatedAt,
    )


@router.get("", response_model=InsiderTradeListResponse)
async def get_all_insider_trades(
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(50, ge=1, le=500, description="Items per page"),
    isin: str | None = Query(None, description="Filter by ISIN"),
    jurisdiction: str | None = Query(None, description="Filter by jurisdiction (DE, CH, US, etc.)"),
    transactionType: str | None = Query(None, description="Filter by transaction type (BUY, SELL)"),
    source: str | None = Query(None, description="Filter by source (ser, bafin, sec)"),
    companyName: str | None = Query(None, description="Filter by company name (partial match)"),
    insiderName: str | None = Query(None, description="Filter by insider name (partial match)"),
    fromDate: datetime | None = Query(None, description="Filter trades from this date"),
    toDate: datetime | None = Query(None, description="Filter trades up to this date"),
    minAmount: float | None = Query(None, description="Minimum transaction amount"),
    maxAmount: float | None = Query(None, description="Maximum transaction amount"),
    excludeNonTrades: bool = Query(False, description="Exclude non-trade transactions (awards, gifts, tax withholdings)"),
) -> InsiderTradeListResponse:
    """Get all insider trades with pagination and filtering."""
    skip = (page - 1) * pageSize
    
    trades = await InsiderTradeService.get_all(
        skip=skip,
        limit=pageSize,
        isin=isin,
        jurisdiction=jurisdiction,
        transaction_type=transactionType,
        source=source,
        company_name=companyName,
        insider_name=insiderName,
        from_date=fromDate,
        to_date=toDate,
        min_amount=minAmount,
        max_amount=maxAmount,
        exclude_non_trades=excludeNonTrades,
    )
    
    total = await InsiderTradeService.count(
        isin=isin,
        jurisdiction=jurisdiction,
        transaction_type=transactionType,
        source=source,
        company_name=companyName,
        insider_name=insiderName,
        from_date=fromDate,
        to_date=toDate,
        min_amount=minAmount,
        max_amount=maxAmount,
        exclude_non_trades=excludeNonTrades,
    )
    
    return InsiderTradeListResponse(
        items=[_trade_to_response(t) for t in trades],
        total=total,
        page=page,
        pageSize=pageSize,
        pages=ceil(total / pageSize) if pageSize > 0 else 0,
    )


@router.get("/by-isin/{isin}", response_model=list[InsiderTradeResponse])
async def get_insider_trades_by_isin(
    isin: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[InsiderTradeResponse]:
    """Get all insider trades for a specific ISIN."""
    trades = await InsiderTradeService.get_by_isin(isin, skip=skip, limit=limit)
    return [_trade_to_response(t) for t in trades]


@router.get("/by-company", response_model=list[InsiderTradeResponse])
async def get_insider_trades_by_company(
    companyName: str = Query(..., description="Company name (partial match)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[InsiderTradeResponse]:
    """Get all insider trades for a specific company."""
    trades = await InsiderTradeService.get_by_company(companyName, skip=skip, limit=limit)
    return [_trade_to_response(t) for t in trades]


@router.get("/recent/{jurisdiction}", response_model=list[InsiderTradeResponse])
async def get_recent_insider_trades(
    jurisdiction: str,
    limit: int = Query(10, ge=1, le=100),
) -> list[InsiderTradeResponse]:
    """Get recent insider trades for a specific jurisdiction."""
    trades = await InsiderTradeService.get_recent_by_jurisdiction(jurisdiction, limit=limit)
    return [_trade_to_response(t) for t in trades]


@router.get("/stats")
async def get_insider_trade_stats(
    isin: str | None = Query(None, description="Filter by ISIN"),
    jurisdiction: str | None = Query(None, description="Filter by jurisdiction"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
) -> dict:
    """Get aggregated statistics for insider trades."""
    return await InsiderTradeService.get_aggregated_stats(
        isin=isin,
        jurisdiction=jurisdiction,
        days=days,
    )


@router.get("/{trade_id}", response_model=InsiderTradeResponse)
async def get_insider_trade(trade_id: str) -> InsiderTradeResponse:
    """Get an insider trade by ID."""
    trade = await InsiderTradeService.get_by_id(trade_id)
    if trade is None:
        raise HTTPException(status_code=404, detail="Insider trade not found")
    return _trade_to_response(trade)


@router.post("", response_model=InsiderTradeResponse, status_code=201)
async def create_insider_trade(data: InsiderTradeCreate) -> InsiderTradeResponse:
    """Create a new insider trade."""
    trade = await InsiderTradeService.create(data)
    return _trade_to_response(trade)


@router.put("/{trade_id}", response_model=InsiderTradeResponse)
async def update_insider_trade(
    trade_id: str,
    data: InsiderTradeUpdate,
) -> InsiderTradeResponse:
    """Update an existing insider trade."""
    trade = await InsiderTradeService.update(trade_id, data)
    if trade is None:
        raise HTTPException(status_code=404, detail="Insider trade not found")
    return _trade_to_response(trade)


@router.delete("/{trade_id}", status_code=204)
async def delete_insider_trade(trade_id: str) -> None:
    """Delete an insider trade by ID."""
    deleted = await InsiderTradeService.delete(trade_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Insider trade not found")
