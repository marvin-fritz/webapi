"""REST API endpoints for Ticker (Insider Trade Signals)."""

import logging
from typing import Literal

from fastapi import APIRouter, Query

from app.schemas.ticker import TickerResponse, TickerSingleNotFoundResponse
from app.services.ticker import TickerService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "",
    response_model=TickerResponse,
    summary="Get insider trading signals",
    description="""
Aggregated insider trading signals identifying interesting stocks.

**Signal Types:**
- `CLUSTER_BUYING`: Multiple insiders buying (≥2 unique buyers)
- `HIGH_VOLUME`: High transaction volume (>100,000)
- `PURE_BUYING`: Only buy transactions, no sells
- `DOMINANT_BUYING`: Buy volume > 2x sell volume

**Use Cases:**
- Identify stocks with unusual insider buying activity
- Detect cluster buying patterns (multiple insiders)
- Screen for high-conviction insider purchases
""",
)
async def get_ticker_signals(
    days: int = Query(
        30,
        ge=1,
        le=365,
        description="Analysis window in days",
    ),
    minTrades: int = Query(
        1,
        ge=1,
        description="Minimum number of trades to include",
    ),
    minTotalAmount: float = Query(
        10000.0,
        ge=0,
        description="Minimum buy volume to include",
    ),
    isin: str | None = Query(
        None,
        description="Filter by ISIN(s), comma-separated for multiple",
    ),
    source: str | None = Query(
        None,
        description="Filter by source (sec, bafin, ser)",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=500,
        description="Maximum number of results",
    ),
) -> TickerResponse:
    """
    Get aggregated insider trading signals.
    
    Returns stocks with significant insider buying activity, sorted by:
    1. Number of unique buyers (cluster buying signal)
    2. Total buy volume
    
    Only considers open market transactions (excludes awards, gifts, etc.).
    """
    # Parse ISIN filter
    isin_filter: list[str] | None = None
    if isin:
        isin_filter = [s.strip() for s in isin.split(",") if s.strip()]

    # Normalize source filter
    source_filter: str | None = None
    if source:
        s_norm = source.strip().lower()
        if s_norm not in ("all", "alles", "*", "any", ""):
            canonical = {"sec": "sec", "bafin": "bafin", "ser": "ser"}.get(s_norm)
            source_filter = canonical if canonical else s_norm

    return await TickerService.get_ticker_signals(
        days=days,
        min_trades=minTrades,
        min_total_amount=minTotalAmount,
        isin_filter=isin_filter,
        source_filter=source_filter,
        limit=limit,
    )


@router.get(
    "/{isin}",
    response_model=TickerResponse,
    responses={
        200: {
            "description": "Ticker signals for the ISIN",
            "model": TickerResponse,
        },
    },
    summary="Get ticker signals for specific ISIN",
    description="""
Get insider trading signals for a specific stock by ISIN.

Returns the same structure as the main endpoint but filtered to a single ISIN.
If no trades or signals are found, returns an empty items list.
""",
)
async def get_ticker_by_isin(
    isin: str,
    days: int = Query(
        30,
        ge=1,
        le=365,
        description="Analysis window in days",
    ),
    minTrades: int = Query(
        1,
        ge=1,
        description="Minimum number of trades",
    ),
    minTotalAmount: float = Query(
        10000.0,
        ge=0,
        description="Minimum buy volume",
    ),
    source: str | None = Query(
        None,
        description="Filter by source (sec, bafin, ser)",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=500,
        description="Maximum results",
    ),
) -> TickerResponse:
    """
    Get ticker signals for a specific ISIN.
    
    Returns insider trading signals for the specified stock.
    """
    # Normalize source filter
    source_filter: str | None = None
    if source:
        s_norm = source.strip().lower()
        if s_norm not in ("all", "alles", "*", "any", ""):
            canonical = {"sec": "sec", "bafin": "bafin", "ser": "ser"}.get(s_norm)
            source_filter = canonical if canonical else s_norm

    response = await TickerService.get_ticker_by_isin(
        isin=isin,
        days=days,
        min_trades=minTrades,
        min_total_amount=minTotalAmount,
        source_filter=source_filter,
        limit=limit,
    )

    return response
