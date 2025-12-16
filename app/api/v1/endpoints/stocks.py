"""REST API endpoints for StockIndex."""

from math import ceil

from fastapi import APIRouter, HTTPException, Query

from app.schemas.stock_index import (
    StockIndexCreate,
    StockIndexListResponse,
    StockIndexResponse,
    StockIndexUpdate,
)
from app.services.stock_index import StockIndexService

router = APIRouter()


def _stock_to_response(stock) -> StockIndexResponse:
    """Convert StockIndex document to response schema."""
    return StockIndexResponse(
        id=str(stock.id),
        name=stock.name,
        identifiers=stock.identifiers,
        ticker=stock.ticker,
        exchangeCode=stock.exchangeCode,
        securityType=stock.securityType,
        marketSector=stock.marketSector,
        scans=stock.scans,
        isin=stock.isin,
        createdAt=stock.createdAt,
        updatedAt=stock.updatedAt,
    )


@router.get("", response_model=StockIndexListResponse)
async def get_all_stocks(
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(50, ge=1, le=500, description="Items per page"),
    isin: str | None = Query(None, description="Filter by ISIN"),
    ticker: str | None = Query(None, description="Filter by ticker (prefix match)"),
    exchangeCode: str | None = Query(None, description="Filter by exchange code (US, GR, etc.)"),
    securityType: str | None = Query(None, description="Filter by security type"),
    name: str | None = Query(None, description="Filter by name (partial match)"),
) -> StockIndexListResponse:
    """Get all stocks with pagination and filtering."""
    skip = (page - 1) * pageSize
    
    stocks = await StockIndexService.get_all(
        skip=skip,
        limit=pageSize,
        isin=isin,
        ticker=ticker,
        exchange_code=exchangeCode,
        security_type=securityType,
        name=name,
    )
    
    total = await StockIndexService.count(
        isin=isin,
        ticker=ticker,
        exchange_code=exchangeCode,
        security_type=securityType,
        name=name,
    )
    
    return StockIndexListResponse(
        items=[_stock_to_response(s) for s in stocks],
        total=total,
        page=page,
        pageSize=pageSize,
        pages=ceil(total / pageSize) if pageSize > 0 else 0,
    )


@router.get("/search", response_model=list[StockIndexResponse])
async def search_stocks(
    q: str = Query(..., min_length=1, description="Search query (name, ticker, or ISIN)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
) -> list[StockIndexResponse]:
    """Search stocks by name, ticker, or ISIN."""
    stocks = await StockIndexService.search(q, limit=limit)
    return [_stock_to_response(s) for s in stocks]


@router.get("/by-isin/{isin}", response_model=StockIndexResponse)
async def get_stock_by_isin(isin: str) -> StockIndexResponse:
    """Get a stock by ISIN."""
    stock = await StockIndexService.get_by_isin(isin)
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return _stock_to_response(stock)


@router.get("/by-ticker/{ticker}", response_model=list[StockIndexResponse])
async def get_stocks_by_ticker(ticker: str) -> list[StockIndexResponse]:
    """Get stocks by ticker (may return multiple for different exchanges)."""
    stocks = await StockIndexService.get_by_ticker(ticker)
    return [_stock_to_response(s) for s in stocks]


@router.get("/by-exchange/{exchange_code}", response_model=list[StockIndexResponse])
async def get_stocks_by_exchange(
    exchange_code: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[StockIndexResponse]:
    """Get all stocks for a specific exchange."""
    stocks = await StockIndexService.get_by_exchange(exchange_code, skip=skip, limit=limit)
    return [_stock_to_response(s) for s in stocks]


@router.get("/{stock_id}", response_model=StockIndexResponse)
async def get_stock(stock_id: str) -> StockIndexResponse:
    """Get a stock by ID."""
    stock = await StockIndexService.get_by_id(stock_id)
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return _stock_to_response(stock)


@router.post("", response_model=StockIndexResponse, status_code=201)
async def create_stock(data: StockIndexCreate) -> StockIndexResponse:
    """Create a new stock index entry."""
    stock = await StockIndexService.create(data)
    return _stock_to_response(stock)


@router.put("/{stock_id}", response_model=StockIndexResponse)
async def update_stock(
    stock_id: str,
    data: StockIndexUpdate,
) -> StockIndexResponse:
    """Update an existing stock index entry."""
    stock = await StockIndexService.update(stock_id, data)
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return _stock_to_response(stock)


@router.delete("/{stock_id}", status_code=204)
async def delete_stock(stock_id: str) -> None:
    """Delete a stock index entry by ID."""
    deleted = await StockIndexService.delete(stock_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Stock not found")
