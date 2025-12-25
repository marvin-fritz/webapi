"""Service for Ticker (Insider Trade Signals) operations."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from app.models.insider_trade import InsiderTrade
from app.schemas.ticker import TickerItem, TickerMeta, TickerResponse, TickerSignal

logger = logging.getLogger(__name__)


class TickerService:
    """Service class for Ticker operations.
    
    Identifies interesting stocks based on insider trading patterns:
    - Cluster buying (multiple insiders buying)
    - High volume transactions
    - Buy/sell ratio analysis
    """

    # Open market transaction methods (both lowercase legacy and uppercase current formats)
    OPEN_MARKET_METHODS = [
        # Lowercase format (legacy)
        "open_market_sale",
        "open_market_purchase",
        # Uppercase format (current)
        "OPEN_MARKET_SALE",
        "OPEN_MARKET_PURCHASE",
        "OPEN_MARKET",
    ]

    @classmethod
    async def get_ticker_signals(
        cls,
        days: int = 30,
        min_trades: int = 1,
        min_total_amount: float = 10000.0,
        isin_filter: list[str] | None = None,
        source_filter: str | None = None,
        limit: int = 100,
    ) -> TickerResponse:
        """
        Get aggregated insider trading signals for stocks.
        
        Args:
            days: Analysis window in days (1-365)
            min_trades: Minimum number of trades
            min_total_amount: Minimum buy volume
            isin_filter: Optional list of ISINs to filter
            source_filter: Optional source filter (sec, bafin, ser)
            limit: Maximum results (1-500)
            
        Returns:
            TickerResponse with metadata and signal items
        """
        now = datetime.now(timezone.utc)
        start_dt = now - timedelta(days=days)

        # Build match stage
        match_stage: dict[str, Any] = {
            "transactionMethod": {"$in": cls.OPEN_MARKET_METHODS},
            "transactionDate": {"$gte": start_dt, "$lte": now},
        }

        if isin_filter:
            if len(isin_filter) == 1:
                match_stage["isin"] = isin_filter[0]
            else:
                match_stage["isin"] = {"$in": isin_filter}

        if source_filter:
            match_stage["source"] = source_filter

        # Aggregation pipeline
        pipeline: list[dict[str, Any]] = [
            {"$match": match_stage},
            # Project and convert types
            {
                "$project": {
                    "isin": 1,
                    "companyName": 1,
                    "insiderName": 1,
                    "transactionType": 1,
                    "transactionDate": 1,
                    "totalAmount": {"$toDouble": "$totalAmount"},
                    "currency": 1,
                }
            },
            # Group by ISIN (company level)
            {
                "$group": {
                    "_id": "$isin",
                    "isin": {"$first": "$isin"},
                    "companyName": {"$first": "$companyName"},
                    "currency": {"$first": "$currency"},
                    "lastTransactionDate": {"$max": "$transactionDate"},
                    "tradeCount": {"$sum": 1},
                    # Buy metrics
                    "buyVolume": {
                        "$sum": {
                            "$cond": [{"$eq": ["$transactionType", "BUY"]}, "$totalAmount", 0]
                        }
                    },
                    "buyCount": {
                        "$sum": {
                            "$cond": [{"$eq": ["$transactionType", "BUY"]}, 1, 0]
                        }
                    },
                    "buyers": {
                        "$addToSet": {
                            "$cond": [
                                {"$eq": ["$transactionType", "BUY"]},
                                "$insiderName",
                                "$$REMOVE",
                            ]
                        }
                    },
                    # Sell metrics
                    "sellVolume": {
                        "$sum": {
                            "$cond": [{"$eq": ["$transactionType", "SELL"]}, "$totalAmount", 0]
                        }
                    },
                    "sellCount": {
                        "$sum": {
                            "$cond": [{"$eq": ["$transactionType", "SELL"]}, 1, 0]
                        }
                    },
                    "sellers": {
                        "$addToSet": {
                            "$cond": [
                                {"$eq": ["$transactionType", "SELL"]},
                                "$insiderName",
                                "$$REMOVE",
                            ]
                        }
                    },
                }
            },
            # Add computed fields
            {
                "$addFields": {
                    "uniqueBuyersCount": {"$size": "$buyers"},
                    "uniqueSellersCount": {"$size": "$sellers"},
                    "netVolume": {"$subtract": ["$buyVolume", "$sellVolume"]},
                }
            },
            # Filter: Looking for buy signals
            {
                "$match": {
                    "buyVolume": {"$gte": min_total_amount},
                    "tradeCount": {"$gte": min_trades},
                }
            },
            # Sort: First by number of buyers (cluster), then by volume
            {"$sort": {"uniqueBuyersCount": -1, "buyVolume": -1}},
            {"$limit": limit},
        ]

        try:
            # Use motor collection directly for Beanie 2.x compatibility
            collection = InsiderTrade.get_pymongo_collection()
            cursor = collection.aggregate(pipeline, allowDiskUse=True)
            docs = await cursor.to_list(length=None)

            # Convert to response items
            items = [cls._doc_to_ticker_item(doc) for doc in docs]

            return TickerResponse(
                meta=TickerMeta(
                    generatedAt=now,
                    windowDays=days,
                    minTrades=min_trades,
                    minTotalAmount=min_total_amount,
                    limit=limit,
                    count=len(items),
                ),
                items=items,
            )

        except Exception as e:
            logger.error(f"Error fetching ticker signals: {e}", exc_info=True)
            # Return empty response on error
            return TickerResponse(
                meta=TickerMeta(
                    generatedAt=now,
                    windowDays=days,
                    minTrades=min_trades,
                    minTotalAmount=min_total_amount,
                    limit=limit,
                    count=0,
                ),
                items=[],
            )

    @classmethod
    async def get_ticker_by_isin(
        cls,
        isin: str,
        days: int = 30,
        min_trades: int = 1,
        min_total_amount: float = 10000.0,
        source_filter: str | None = None,
        limit: int = 100,
    ) -> TickerResponse | None:
        """
        Get ticker signals for a specific ISIN.
        
        Args:
            isin: The ISIN to analyze
            days: Analysis window in days
            min_trades: Minimum number of trades
            min_total_amount: Minimum buy volume
            source_filter: Optional source filter
            limit: Maximum results
            
        Returns:
            TickerResponse or None if no data/signals found
        """
        response = await cls.get_ticker_signals(
            days=days,
            min_trades=min_trades,
            min_total_amount=min_total_amount,
            isin_filter=[isin.strip()],
            source_filter=source_filter,
            limit=limit,
        )

        # Add single ISIN to meta
        response.meta.singleIsin = isin.strip()

        return response

    @classmethod
    def _doc_to_ticker_item(cls, doc: dict[str, Any]) -> TickerItem:
        """Convert aggregation document to TickerItem."""
        isin = doc.get("isin", "")
        company_name = doc.get("companyName", isin or "Unbekannt")
        currency = doc.get("currency", "")
        last_tx_date = doc.get("lastTransactionDate")
        
        buy_volume = float(doc.get("buyVolume", 0) or 0)
        sell_volume = float(doc.get("sellVolume", 0) or 0)
        unique_buyers = int(doc.get("uniqueBuyersCount", 0) or 0)
        buyers_list = doc.get("buyers", []) or []
        sellers_list = doc.get("sellers", []) or []

        # Generate signals
        signals = cls._generate_signals(unique_buyers, buy_volume, sell_volume)

        # Generate headline
        headline = cls._generate_headline(
            unique_buyers, buyers_list, buy_volume, currency, company_name
        )

        # Generate UID
        uid = f"TICKER-{isin}-{last_tx_date.isoformat() if last_tx_date else 'unknown'}"

        return TickerItem(
            uid=uid,
            isin=isin,
            companyName=company_name,
            currency=currency,
            lastTransactionDate=last_tx_date,
            tradeCount=int(doc.get("tradeCount", 0) or 0),
            buyCount=int(doc.get("buyCount", 0) or 0),
            sellCount=int(doc.get("sellCount", 0) or 0),
            buyVolume=buy_volume,
            sellVolume=sell_volume,
            netVolume=float(doc.get("netVolume", 0) or 0),
            uniqueBuyersCount=unique_buyers,
            uniqueSellersCount=int(doc.get("uniqueSellersCount", 0) or 0),
            buyers=buyers_list,
            sellers=sellers_list,
            signals=signals,
            headline=headline,
        )

    @classmethod
    def _generate_signals(
        cls,
        unique_buyers: int,
        buy_volume: float,
        sell_volume: float,
    ) -> list[TickerSignal]:
        """Generate trading signals based on metrics."""
        signals = []

        if unique_buyers >= 2:
            signals.append(TickerSignal.CLUSTER_BUYING)

        if buy_volume > 100000:
            signals.append(TickerSignal.HIGH_VOLUME)

        if sell_volume == 0 and buy_volume > 0:
            signals.append(TickerSignal.PURE_BUYING)
        elif buy_volume > (sell_volume * 2):
            signals.append(TickerSignal.DOMINANT_BUYING)

        return signals

    @classmethod
    def _generate_headline(
        cls,
        unique_buyers: int,
        buyers_list: list[str],
        buy_volume: float,
        currency: str,
        company_name: str,
    ) -> str:
        """Generate human-readable headline."""
        # Format buyers string
        if buyers_list:
            buyers_str = ", ".join(buyers_list[:2])
            if len(buyers_list) > 2:
                buyers_str += f" und {len(buyers_list) - 2} weitere"
        else:
            buyers_str = "unbekannt"

        return (
            f"{unique_buyers} Insider ({buyers_str}) kauften für "
            f"{buy_volume:,.0f} {currency} Anteile von {company_name}."
        )
