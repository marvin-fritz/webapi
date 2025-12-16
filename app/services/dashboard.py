"""Service for Dashboard Statistics."""

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from app.models.insider_trade import InsiderTrade
from app.schemas.dashboard import (
    DashboardStatsResponse,
    ExtendedStats,
    InsiderTradesStats,
    JurisdictionStats,
    ProcessedPerHour,
    ProcessingStats,
    QuickStatsResponse,
    TimeRange,
    TopInsider,
    TopTicker,
    TradesByType,
    VolumeByCurrency,
)

logger = logging.getLogger(__name__)


class DashboardService:
    """Service class for Dashboard Statistics operations."""

    # Transaction methods to exclude from buy/sell counts
    EXCLUDED_METHODS = [
        # Lowercase format
        "award_or_grant",
        "gift",
        "tax_withholding_or_exercise_cost",
        "conversion",
        "exercise",
        "transfer",
        # Uppercase format
        "AWARD",
        "GIFT",
        "OPTION_EXERCISE",
        "OPTION_EXPIRATION",
        "CONVERSION",
        "TAX_WITHHOLDING",
        "TRANSFER",
        "GRANT",
        "EXERCISE",
    ]

    @classmethod
    async def get_dashboard_stats(
        cls,
        hours: int = 24,
        tz: str = "Europe/Berlin",
        include_extended: bool = True,
    ) -> DashboardStatsResponse:
        """
        Get comprehensive dashboard statistics for the specified time range.
        
        Args:
            hours: Time range in hours (1-336)
            tz: Timezone string for display
            include_extended: Whether to include extended statistics
            
        Returns:
            DashboardStatsResponse with all statistics
        """
        now = datetime.now(timezone.utc)
        from_date = now - timedelta(hours=hours)

        # Build match filter - use filingDate for "recent" data
        # (transactionDate is when the trade happened, often weeks before filing)
        match_filter: dict[str, Any] = {
            "filingDate": {"$gte": from_date},
        }

        # Main aggregation pipeline
        pipeline = [
            {"$match": match_filter},
            {
                "$facet": {
                    # Basic counts
                    "totalCount": [{"$count": "count"}],
                    
                    # By transaction type (only real trades)
                    "byType": [
                        {
                            "$match": {
                                "transactionMethod": {"$nin": cls.EXCLUDED_METHODS}
                            }
                        },
                        {
                            "$group": {
                                "_id": "$transactionType",
                                "count": {"$sum": 1},
                            }
                        },
                    ],
                    
                    # Unique stocks (ISINs)
                    "uniqueStocks": [
                        {"$group": {"_id": "$isin"}},
                        {"$count": "count"},
                    ],
                    
                    # Top tickers by count
                    "topTickers": [
                        {
                            "$match": {
                                "transactionMethod": {"$nin": cls.EXCLUDED_METHODS}
                            }
                        },
                        {
                            "$group": {
                                "_id": "$isin",
                                "ticker": {"$first": "$ticker"},
                                "companyName": {"$first": "$companyName"},
                                "jurisdiction": {"$first": "$jurisdiction"},
                                "count": {"$sum": 1},
                            }
                        },
                        {"$sort": {"count": -1}},
                        {"$limit": 20},
                    ],
                    
                    # Volume by currency
                    "volumeByCurrency": [
                        {
                            "$match": {
                                "transactionMethod": {"$nin": cls.EXCLUDED_METHODS},
                                "currency": {"$exists": True, "$ne": None},
                                "totalAmount": {"$exists": True, "$ne": None},
                            }
                        },
                        {
                            "$group": {
                                "_id": "$currency",
                                "totalVolume": {"$sum": "$totalAmount"},
                                "count": {"$sum": 1},
                            }
                        },
                        {"$sort": {"totalVolume": -1}},
                    ],
                    
                    # Hourly breakdown (by filing date = when reported)
                    "hourlyBreakdown": [
                        {
                            "$group": {
                                "_id": {
                                    "$dateToString": {
                                        "format": "%Y-%m-%dT%H:00:00.000Z",
                                        "date": "$filingDate",
                                    }
                                },
                                "tradesCount": {"$sum": 1},
                                "uniqueStocks": {"$addToSet": "$isin"},
                            }
                        },
                        {
                            "$project": {
                                "_id": 1,
                                "tradesCount": 1,
                                "count": {"$size": "$uniqueStocks"},
                            }
                        },
                        {"$sort": {"_id": 1}},
                    ],
                    
                    # By jurisdiction
                    "byJurisdiction": [
                        {
                            "$match": {
                                "transactionMethod": {"$nin": cls.EXCLUDED_METHODS}
                            }
                        },
                        {
                            "$group": {
                                "_id": "$jurisdiction",
                                "trades": {"$sum": 1},
                                "buys": {
                                    "$sum": {
                                        "$cond": [
                                            {"$eq": ["$transactionType", "BUY"]},
                                            1,
                                            0,
                                        ]
                                    }
                                },
                                "sells": {
                                    "$sum": {
                                        "$cond": [
                                            {"$eq": ["$transactionType", "SELL"]},
                                            1,
                                            0,
                                        ]
                                    }
                                },
                            }
                        },
                        {"$sort": {"trades": -1}},
                    ],
                    
                    # Top insiders
                    "topInsiders": [
                        {
                            "$match": {
                                "transactionMethod": {"$nin": cls.EXCLUDED_METHODS},
                                "insiderName": {"$exists": True, "$ne": None},
                            }
                        },
                        {
                            "$group": {
                                "_id": "$insiderName",
                                "companyName": {"$first": "$companyName"},
                                "transactions": {"$sum": 1},
                                "buys": {
                                    "$sum": {
                                        "$cond": [
                                            {"$eq": ["$transactionType", "BUY"]},
                                            1,
                                            0,
                                        ]
                                    }
                                },
                                "sells": {
                                    "$sum": {
                                        "$cond": [
                                            {"$eq": ["$transactionType", "SELL"]},
                                            1,
                                            0,
                                        ]
                                    }
                                },
                                "totalVolume": {"$sum": "$totalAmount"},
                            }
                        },
                        {"$sort": {"transactions": -1}},
                        {"$limit": 10},
                    ],
                }
            },
        ]

        # Use motor collection directly for Beanie 2.x compatibility
        collection = InsiderTrade.get_pymongo_collection()
        cursor = collection.aggregate(pipeline, allowDiskUse=True)
        results = await cursor.to_list(length=None)
        
        if not results:
            logger.warning(f"Dashboard aggregation returned no results for {hours}h")
            return cls._empty_response(from_date, now, hours, tz)
        
        try:
            
            data = results[0]
            
            # Parse results
            total_trades = data["totalCount"][0]["count"] if data["totalCount"] else 0
            processed_stocks = data["uniqueStocks"][0]["count"] if data["uniqueStocks"] else 0
            
            # By type
            buy_count = 0
            sell_count = 0
            for item in data.get("byType", []):
                if item["_id"] == "BUY":
                    buy_count = item["count"]
                elif item["_id"] == "SELL":
                    sell_count = item["count"]
            
            # Top tickers
            top_tickers = [
                TopTicker(
                    ticker=item.get("ticker") or item["_id"] or "N/A",
                    companyName=item.get("companyName"),
                    count=item["count"],
                    isin=item["_id"],
                    jurisdiction=item.get("jurisdiction"),
                )
                for item in data.get("topTickers", [])
            ]
            
            # Volume by currency
            volume_by_currency = []
            for item in data.get("volumeByCurrency", []):
                if item["_id"] and item["count"] > 0:
                    volume_by_currency.append(VolumeByCurrency(
                        currency=str(item["_id"]),
                        totalVolume=float(item.get("totalVolume", 0) or 0),
                        avgVolume=float(item.get("totalVolume", 0) or 0) / item["count"],
                        count=item["count"],
                    ))
            
            # Hourly breakdown
            processed_per_hour = [
                ProcessedPerHour(
                    hour=item["_id"],
                    count=item.get("count", 0),
                    tradesCount=item.get("tradesCount", 0),
                )
                for item in data.get("hourlyBreakdown", [])
            ]
            
            # Find most active hour
            most_active_hour = None
            most_active_hour_count = 0
            for item in processed_per_hour:
                if item.tradesCount > most_active_hour_count:
                    most_active_hour = item.hour
                    most_active_hour_count = item.tradesCount
            
            # Extended stats
            extended = None
            if include_extended:
                # By jurisdiction
                by_jurisdiction = []
                for item in data.get("byJurisdiction", []):
                    if item["_id"]:
                        total = item["buys"] + item["sells"]
                        by_jurisdiction.append(JurisdictionStats(
                            jurisdiction=item["_id"],
                            trades=item["trades"],
                            buys=item["buys"],
                            sells=item["sells"],
                            buyRatio=round((item["buys"] / total * 100) if total > 0 else 50.0, 2),
                        ))
                
                # Top insiders
                top_insiders = [
                    TopInsider(
                        insiderName=item["_id"],
                        companyName=item.get("companyName"),
                        transactions=item["transactions"],
                        buys=item["buys"],
                        sells=item["sells"],
                        totalVolume=float(item.get("totalVolume", 0) or 0),
                    )
                    for item in data.get("topInsiders", [])
                    if item["_id"]
                ]
                
                total_relevant = buy_count + sell_count
                extended = ExtendedStats(
                    byJurisdiction=by_jurisdiction,
                    topInsiders=top_insiders,
                    avgTradesPerStock=round(total_trades / processed_stocks, 2) if processed_stocks > 0 else 0.0,
                    buyPercentage=round((buy_count / total_relevant * 100) if total_relevant > 0 else 50.0, 2),
                    mostActiveHour=most_active_hour,
                    mostActiveHourCount=most_active_hour_count,
                )
            
            return DashboardStatsResponse(
                timeRange=TimeRange(
                    **{"from": from_date.isoformat(), "to": now.isoformat()},
                    timezone=tz,
                    hours=hours,
                ),
                processing=ProcessingStats(
                    processedStocks=processed_stocks,
                    totalTrades=total_trades,
                    processedPerHour=processed_per_hour,
                ),
                insiderTrades=InsiderTradesStats(
                    newTrades=buy_count + sell_count,
                    byType=TradesByType(BUY=buy_count, SELL=sell_count),
                    topTickersByCount=top_tickers,
                    volumeByCurrency=volume_by_currency,
                ),
                extended=extended,
            )
            
        except Exception as e:
            logger.error(f"Error fetching dashboard stats: {e}", exc_info=True)
            return cls._empty_response(from_date, now, hours, tz)

    @classmethod
    async def get_quick_stats(cls, hours: int = 24) -> QuickStatsResponse:
        """
        Get lightweight quick stats for dashboard widgets.
        
        Args:
            hours: Time range in hours
            
        Returns:
            QuickStatsResponse with key metrics
        """
        now = datetime.now(timezone.utc)
        from_date = now - timedelta(hours=hours)
        
        # Previous period for trend comparison
        prev_from = from_date - timedelta(hours=hours)
        
        # Use filingDate for recent data (transactionDate is when trade happened, often weeks earlier)
        match_filter: dict[str, Any] = {
            "filingDate": {"$gte": from_date},
            "transactionMethod": {"$nin": cls.EXCLUDED_METHODS},
        }
        
        pipeline = [
            {"$match": match_filter},
            {
                "$facet": {
                    "counts": [
                        {
                            "$group": {
                                "_id": None,
                                "total": {"$sum": 1},
                                "buys": {
                                    "$sum": {"$cond": [{"$eq": ["$transactionType", "BUY"]}, 1, 0]}
                                },
                                "sells": {
                                    "$sum": {"$cond": [{"$eq": ["$transactionType", "SELL"]}, 1, 0]}
                                },
                                "uniqueStocks": {"$addToSet": "$isin"},
                            }
                        },
                    ],
                    "topTicker": [
                        {"$group": {"_id": "$ticker", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}},
                        {"$limit": 1},
                    ],
                }
            },
        ]
        
        # Previous period pipeline for trend
        prev_pipeline = [
            {
                "$match": {
                    "filingDate": {"$gte": prev_from, "$lt": from_date},
                    "transactionMethod": {"$nin": cls.EXCLUDED_METHODS},
                }
            },
            {"$count": "count"},
        ]
        
        try:
            collection = InsiderTrade.get_pymongo_collection()
            
            # Current period
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Previous period for trend
            prev_cursor = collection.aggregate(prev_pipeline)
            prev_results = await prev_cursor.to_list(length=None)
            
            prev_count = prev_results[0]["count"] if prev_results else 0
            
            if not results or not results[0].get("counts"):
                return QuickStatsResponse(
                    generatedAt=now.isoformat(),
                    hours=hours,
                    trendDirection="neutral",
                )
            
            data = results[0]
            counts = data["counts"][0] if data["counts"] else {}
            top_ticker_data = data["topTicker"][0] if data["topTicker"] else {}
            
            total = counts.get("total", 0)
            buys = counts.get("buys", 0)
            sells = counts.get("sells", 0)
            unique_stocks = len(counts.get("uniqueStocks", []))
            
            # Trend direction
            if prev_count > 0:
                change = (total - prev_count) / prev_count
                if change > 0.1:
                    trend = "up"
                elif change < -0.1:
                    trend = "down"
                else:
                    trend = "neutral"
            else:
                trend = "up" if total > 0 else "neutral"
            
            return QuickStatsResponse(
                generatedAt=now.isoformat(),
                hours=hours,
                totalTrades=buys + sells,
                processedStocks=unique_stocks,
                buys=buys,
                sells=sells,
                buyPercentage=round((buys / (buys + sells) * 100) if (buys + sells) > 0 else 50.0, 2),
                topTicker=top_ticker_data.get("_id"),
                topTickerCount=top_ticker_data.get("count", 0),
                trendDirection=trend,
            )
            
        except Exception as e:
            logger.error(f"Error fetching quick stats: {e}", exc_info=True)
            return QuickStatsResponse(
                generatedAt=now.isoformat(),
                hours=hours,
                trendDirection="neutral",
            )

    @classmethod
    def _empty_response(
        cls,
        from_date: datetime,
        to_date: datetime,
        hours: int,
        tz: str,
    ) -> DashboardStatsResponse:
        """Create an empty response when no data is available."""
        return DashboardStatsResponse(
            timeRange=TimeRange(
                **{"from": from_date.isoformat(), "to": to_date.isoformat()},
                timezone=tz,
                hours=hours,
            ),
            processing=ProcessingStats(),
            insiderTrades=InsiderTradesStats(),
            extended=ExtendedStats(),
        )
