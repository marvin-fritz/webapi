"""Service for Insider Trading Sentiment Analysis.

Berechnet verschiedene Sentiment-Indikatoren basierend auf Insider-Trading-Aktivitäten:
1. Insider-Indikator: Anteil Käufe an Gesamt-Transaktionen (28-Tage gleitend)
2. Insiderkauf-Barometer: Abweichung vom 12-Monats-Durchschnitt
3. Insider-Aktivitätsanzeige: Durchschnittliche Transaktionen pro Tag
4. Marktbreite-Analyse: Sektor-, Jurisdiktion- und Volumen-basierte Metriken
5. Top-Mover: Unternehmen mit höchster Insider-Aktivität
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from app.models.insider_trade import InsiderTrade

logger = logging.getLogger(__name__)


class SentimentService:
    """Service class for Sentiment Analysis operations."""

    # Konstanten
    INDICATOR_WINDOW_DAYS = 28  # Fenster für gleitenden Durchschnitt
    REFERENCE_PERIOD_DAYS = 365  # 12 Monate Referenzzeitraum
    MAX_HISTORY_DAYS = 730  # 2 Jahre maximale Historie
    SHORT_TERM_WINDOW = 7  # Kurzfrist-Fenster für Momentum
    MEDIUM_TERM_WINDOW = 90  # Mittelfrist für Trends

    @classmethod
    async def calculate_sentiment(
        cls,
        days: int,
        jurisdiction: str | None = None,
    ) -> dict[str, Any]:
        """
        Berechnet vollständige Sentiment-Analyse mit Historie.

        Args:
            days: Anzahl Tage für Historie
            jurisdiction: Optional - Filter nach Land

        Returns:
            Dictionary mit allen Sentiment-Daten
        """
        now = datetime.now(timezone.utc)

        # Zeitraum: Wir brauchen extra Daten für gleitenden Durchschnitt
        # Plus Referenzzeitraum für Barometer-Berechnung
        total_lookback = days + cls.INDICATOR_WINDOW_DAYS + cls.REFERENCE_PERIOD_DAYS
        from_date = now - timedelta(days=total_lookback)

        # Tägliche Transaktionsdaten holen
        daily_data_sparse = await cls._get_daily_transaction_data(from_date, jurisdiction)

        # Fehlende Tage mit 0 füllen
        daily_data = cls._fill_daily_data(daily_data_sparse, from_date, now)

        # Zeitreihen berechnen
        indicator_series = cls._calculate_indicator_series(daily_data, days)
        barometer_series = cls._calculate_barometer_series(daily_data, days)
        activity_series = cls._calculate_activity_series(daily_data, days)

        # Aktuelle Werte
        current = cls._get_current_values(daily_data)

        # Zusätzliche Markt-Statistiken berechnen
        market_stats = cls._calculate_market_statistics(daily_data, days)

        # Response zusammenstellen
        return {
            "metadata": {
                "generatedAt": now.isoformat(),
                "timeRange": {
                    "days": days,
                    "from": (now - timedelta(days=days)).isoformat(),
                    "to": now.isoformat(),
                },
                "jurisdiction": jurisdiction or "ALL",
                "parameters": {
                    "indicatorWindow": cls.INDICATOR_WINDOW_DAYS,
                    "referencePeriod": cls.REFERENCE_PERIOD_DAYS,
                },
                "dataPoints": len(indicator_series),
            },
            "current": current,
            "timeSeries": {
                "insiderIndicator": indicator_series,
                "insiderBarometer": barometer_series,
                "activityIndicator": activity_series,
            },
            "marketStatistics": market_stats,
        }

    @classmethod
    async def get_current_sentiment(
        cls,
        jurisdiction: str | None = None,
    ) -> dict[str, Any]:
        """Schnelle Berechnung nur der aktuellen Werte."""
        now = datetime.now(timezone.utc)

        # Nur benötigte Daten holen
        lookback = cls.INDICATOR_WINDOW_DAYS + cls.REFERENCE_PERIOD_DAYS
        from_date = now - timedelta(days=lookback)

        daily_data = await cls._get_daily_transaction_data(from_date, jurisdiction)
        daily_data = cls._fill_daily_data(daily_data, from_date, now)
        current = cls._get_current_values(daily_data)

        return {
            "metadata": {
                "generatedAt": now.isoformat(),
                "jurisdiction": jurisdiction or "ALL",
            },
            "current": current,
        }

    @classmethod
    async def calculate_market_breadth(
        cls,
        days: int,
        jurisdiction: str | None = None,
    ) -> dict[str, Any]:
        """
        Berechnet Marktbreite-Analyse über verschiedene Dimensionen.
        """
        now = datetime.now(timezone.utc)
        from_date = now - timedelta(days=days)

        # Filter aufbauen
        match_filter: dict[str, Any] = {"transactionDate": {"$gte": from_date}}
        if jurisdiction:
            match_filter["jurisdiction"] = jurisdiction.upper()

        # Pipeline für Marktbreite-Analyse
        pipeline = [
            {"$match": match_filter},
            # Felder projizieren
            {
                "$project": {
                    "_id": 0,
                    "isin": 1,
                    "companyName": 1,
                    "jurisdiction": 1,
                    "transactionType": 1,
                    "transactionMethod": 1,
                    "totalAmount": 1,
                    "shares": 1,
                    "transactionDate": 1,
                }
            },
            # Nach ISIN gruppieren
            {
                "$group": {
                    "_id": "$isin",
                    "companyName": {"$first": "$companyName"},
                    "jurisdiction": {"$first": "$jurisdiction"},
                    "transactionCount": {"$sum": 1},
                    "buyCount": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$eq": ["$transactionType", "BUY"]},
                                        {
                                            "$not": [
                                                {
                                                    "$in": [
                                                        "$transactionMethod",
                                                        [
                                                            "award_or_grant",
                                                            "gift",
                                                            "tax_withholding_or_exercise_cost",
                                                            "AWARD",
                                                            "GIFT",
                                                            "OPTION_EXERCISE",
                                                            "TAX_WITHHOLDING",
                                                        ],
                                                    ]
                                                }
                                            ]
                                        },
                                    ]
                                },
                                1,
                                0,
                            ]
                        }
                    },
                    "sellCount": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$eq": ["$transactionType", "SELL"]},
                                        {
                                            "$not": [
                                                {
                                                    "$in": [
                                                        "$transactionMethod",
                                                        [
                                                            "award_or_grant",
                                                            "gift",
                                                            "tax_withholding_or_exercise_cost",
                                                            "AWARD",
                                                            "GIFT",
                                                            "OPTION_EXERCISE",
                                                            "TAX_WITHHOLDING",
                                                        ],
                                                    ]
                                                }
                                            ]
                                        },
                                    ]
                                },
                                1,
                                0,
                            ]
                        }
                    },
                    "totalVolume": {"$sum": "$totalAmount"},
                    "lastTransactionDate": {"$max": "$transactionDate"},
                }
            },
            {"$sort": {"transactionCount": -1}},
            {"$limit": 100},
        ]

        isin_data = await InsiderTrade.aggregate(pipeline, allowDiskUse=True).to_list()

        # Jurisdiktions-Verteilung
        jurisdiction_stats: dict[str, dict[str, int]] = defaultdict(
            lambda: {"buys": 0, "sells": 0, "transactions": 0}
        )
        for item in isin_data:
            juris = item.get("jurisdiction", "UNKNOWN")
            jurisdiction_stats[juris]["transactions"] += item["transactionCount"]
            jurisdiction_stats[juris]["buys"] += item["buyCount"]
            jurisdiction_stats[juris]["sells"] += item["sellCount"]

        # Top ISINs nach Aktivität
        top_isins = []
        for item in isin_data[:20]:
            relevant_tx = item["buyCount"] + item["sellCount"]
            buy_ratio = (item["buyCount"] / relevant_tx * 100) if relevant_tx > 0 else 50
            top_isins.append(
                {
                    "isin": item["_id"],
                    "companyName": item["companyName"],
                    "jurisdiction": item["jurisdiction"],
                    "transactions": item["transactionCount"],
                    "buys": item["buyCount"],
                    "sells": item["sellCount"],
                    "buyRatio": round(buy_ratio, 2),
                    "sentiment": (
                        "bullish" if buy_ratio > 60 else ("bearish" if buy_ratio < 40 else "neutral")
                    ),
                    "lastActivity": (
                        item["lastTransactionDate"].isoformat()
                        if item.get("lastTransactionDate")
                        else None
                    ),
                }
            )

        # Markt-Breite-Scores
        total_companies = len(isin_data)

        def get_sentiment_ratio(item: dict) -> float:
            relevant = item["buyCount"] + item["sellCount"]
            return (item["buyCount"] / relevant * 100) if relevant > 0 else 50

        bullish_companies = len([i for i in isin_data if get_sentiment_ratio(i) > 60])
        bearish_companies = len([i for i in isin_data if get_sentiment_ratio(i) < 40])
        neutral_companies = total_companies - bullish_companies - bearish_companies

        return {
            "metadata": {
                "generatedAt": now.isoformat(),
                "days": days,
                "jurisdiction": jurisdiction or "ALL",
            },
            "breadthMetrics": {
                "totalActiveCompanies": total_companies,
                "bullishCompanies": bullish_companies,
                "bearishCompanies": bearish_companies,
                "neutralCompanies": neutral_companies,
                "breadthRatio": (
                    round(bullish_companies / bearish_companies, 2)
                    if bearish_companies > 0
                    else (999.99 if bullish_companies > 0 else 1.0)
                ),
            },
            "jurisdictionBreakdown": [
                {
                    "jurisdiction": k,
                    "transactions": v["transactions"],
                    "buys": v["buys"],
                    "sells": v["sells"],
                    "buyRatio": round(
                        (v["buys"] / (v["buys"] + v["sells"]) * 100)
                        if (v["buys"] + v["sells"]) > 0
                        else 50,
                        2,
                    ),
                }
                for k, v in sorted(
                    jurisdiction_stats.items(),
                    key=lambda x: x[1]["transactions"],
                    reverse=True,
                )
            ],
            "topActiveCompanies": top_isins,
        }

    @classmethod
    async def get_top_movers(
        cls,
        days: int,
        limit: int,
        jurisdiction: str | None = None,
        min_transactions: int = 3,
    ) -> dict[str, Any]:
        """Identifiziert ISINs mit höchster Insider-Aktivität."""
        now = datetime.now(timezone.utc)
        from_date = now - timedelta(days=days)

        match_filter: dict[str, Any] = {"transactionDate": {"$gte": from_date}}
        if jurisdiction:
            match_filter["jurisdiction"] = jurisdiction.upper()

        pipeline = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": "$isin",
                    "companyName": {"$first": "$companyName"},
                    "jurisdiction": {"$first": "$jurisdiction"},
                    "transactions": {"$sum": 1},
                    "buys": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$eq": ["$transactionType", "BUY"]},
                                        {
                                            "$not": [
                                                {
                                                    "$in": [
                                                        "$transactionMethod",
                                                        [
                                                            "award_or_grant",
                                                            "gift",
                                                            "tax_withholding_or_exercise_cost",
                                                            "AWARD",
                                                            "GIFT",
                                                            "OPTION_EXERCISE",
                                                            "TAX_WITHHOLDING",
                                                        ],
                                                    ]
                                                }
                                            ]
                                        },
                                    ]
                                },
                                1,
                                0,
                            ]
                        }
                    },
                    "sells": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$eq": ["$transactionType", "SELL"]},
                                        {
                                            "$not": [
                                                {
                                                    "$in": [
                                                        "$transactionMethod",
                                                        [
                                                            "award_or_grant",
                                                            "gift",
                                                            "tax_withholding_or_exercise_cost",
                                                            "AWARD",
                                                            "GIFT",
                                                            "OPTION_EXERCISE",
                                                            "TAX_WITHHOLDING",
                                                        ],
                                                    ]
                                                }
                                            ]
                                        },
                                    ]
                                },
                                1,
                                0,
                            ]
                        }
                    },
                    "uniqueInsiders": {"$addToSet": "$insiderName"},
                    "totalVolume": {"$sum": "$totalAmount"},
                    "avgPrice": {"$avg": "$pricePerShare"},
                    "lastDate": {"$max": "$transactionDate"},
                }
            },
            # Filter: Mindestanzahl Transaktionen
            {"$match": {"transactions": {"$gte": min_transactions}}},
            # Sortierung: Aktivität (Transaktionen * Insider-Anzahl)
            {
                "$addFields": {
                    "activityScore": {
                        "$multiply": ["$transactions", {"$size": "$uniqueInsiders"}]
                    },
                    "buyRatio": {
                        "$cond": [
                            {"$gt": [{"$add": ["$buys", "$sells"]}, 0]},
                            {
                                "$multiply": [
                                    {"$divide": ["$buys", {"$add": ["$buys", "$sells"]}]},
                                    100,
                                ]
                            },
                            50,
                        ]
                    },
                }
            },
            {"$sort": {"activityScore": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "isin": "$_id",
                    "companyName": 1,
                    "jurisdiction": 1,
                    "transactions": 1,
                    "buys": 1,
                    "sells": 1,
                    "buyRatio": {"$round": ["$buyRatio", 2]},
                    "uniqueInsiders": {"$size": "$uniqueInsiders"},
                    "activityScore": 1,
                    "sentiment": {
                        "$switch": {
                            "branches": [
                                {"case": {"$gte": ["$buyRatio", 70]}, "then": "strong_bullish"},
                                {"case": {"$gte": ["$buyRatio", 55]}, "then": "bullish"},
                                {"case": {"$gte": ["$buyRatio", 45]}, "then": "neutral"},
                                {"case": {"$gte": ["$buyRatio", 30]}, "then": "bearish"},
                            ],
                            "default": "strong_bearish",
                        }
                    },
                    "lastActivity": "$lastDate",
                }
            },
        ]

        movers = await InsiderTrade.aggregate(pipeline, allowDiskUse=True).to_list()

        # ISO-Format für Daten
        for mover in movers:
            if mover.get("lastActivity"):
                mover["lastActivity"] = mover["lastActivity"].isoformat()

        return {
            "metadata": {
                "generatedAt": now.isoformat(),
                "days": days,
                "limit": limit,
                "minTransactions": min_transactions,
                "jurisdiction": jurisdiction or "ALL",
                "resultCount": len(movers),
            },
            "topMovers": movers,
        }

    @classmethod
    async def calculate_trends(
        cls,
        jurisdiction: str | None = None,
    ) -> dict[str, Any]:
        """Vergleicht Sentiment über verschiedene Zeitfenster."""
        now = datetime.now(timezone.utc)

        # Verschiedene Zeitfenster
        windows = {
            "7d": 7,
            "28d": 28,
            "90d": 90,
            "365d": 365,
        }

        trends: dict[str, dict[str, Any]] = {}

        for window_name, window_days in windows.items():
            from_date = now - timedelta(days=window_days + cls.INDICATOR_WINDOW_DAYS)
            daily_data = await cls._get_daily_transaction_data(from_date, jurisdiction)

            if daily_data:
                daily_data = cls._fill_daily_data(daily_data, from_date, now)
                # Nur aktuelle Werte für dieses Fenster
                indicator_series = cls._calculate_indicator_series(daily_data, window_days)

                if indicator_series:
                    recent_values = [s["value"] for s in indicator_series[-7:]]
                    avg_indicator = (
                        sum(recent_values) / len(recent_values) if recent_values else 50.0
                    )

                    total_buys = sum(s["buys"] for s in indicator_series[-7:])
                    total_sells = sum(s["sells"] for s in indicator_series[-7:])

                    trends[window_name] = {
                        "avgIndicator": round(avg_indicator, 2),
                        "recentBuys": total_buys,
                        "recentSells": total_sells,
                        "sentiment": cls._interpret_value(avg_indicator),
                    }
                else:
                    trends[window_name] = {
                        "avgIndicator": 50.0,
                        "recentBuys": 0,
                        "recentSells": 0,
                        "sentiment": "neutral",
                    }
            else:
                trends[window_name] = {
                    "avgIndicator": 50.0,
                    "recentBuys": 0,
                    "recentSells": 0,
                    "sentiment": "neutral",
                }

        # Momentum-Berechnung
        momentum: dict[str, float] = {}
        if "7d" in trends and "28d" in trends:
            momentum["shortTerm"] = round(
                trends["7d"]["avgIndicator"] - trends["28d"]["avgIndicator"], 2
            )
        if "28d" in trends and "90d" in trends:
            momentum["mediumTerm"] = round(
                trends["28d"]["avgIndicator"] - trends["90d"]["avgIndicator"], 2
            )
        if "90d" in trends and "365d" in trends:
            momentum["longTerm"] = round(
                trends["90d"]["avgIndicator"] - trends["365d"]["avgIndicator"], 2
            )

        return {
            "metadata": {
                "generatedAt": now.isoformat(),
                "jurisdiction": jurisdiction or "ALL",
            },
            "trends": trends,
            "momentum": momentum,
            "interpretation": cls._interpret_momentum(momentum),
        }

    # --- Private Helper Methods ---

    @classmethod
    async def _get_daily_transaction_data(
        cls,
        from_date: datetime,
        jurisdiction: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Holt tägliche aggregierte Transaktionsdaten.

        Deduplizierung: Mehrere Transaktionen des gleichen Insiders am gleichen Tag
        werden nur einmal gezählt.
        """
        try:
            # Filter aufbauen
            match_filter: dict[str, Any] = {"transactionDate": {"$gte": from_date}}

            if jurisdiction:
                match_filter["jurisdiction"] = jurisdiction.upper()

            # Pipeline für tägliche Aggregation mit Deduplizierung
            pipeline = [
                {"$match": match_filter},
                # Nur relevante Felder
                {
                    "$project": {
                        "_id": 0,
                        "date": "$transactionDate",
                        "type": "$transactionType",
                        "acq": "$transactionMethod",
                        "person": "$insiderName",
                        "isin": "$isin",
                        "isOfficer": 1,
                        "isDirector": 1,
                        "jurisdiction": 1,
                    }
                },
                # Deduplizierung: Group by Date + Person + ISIN
                {
                    "$group": {
                        "_id": {
                            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                            "person": "$person",
                            "isin": "$isin",
                        },
                        # Erste Transaktion des Tages pro Person/Aktie nehmen
                        "type": {"$first": "$type"},
                        "acq": {"$first": "$acq"},
                        "isOfficer": {"$first": "$isOfficer"},
                        "isDirector": {"$first": "$isDirector"},
                        "jurisdiction": {"$first": "$jurisdiction"},
                    }
                },
                # Klassifizierung als Buy oder Sell
                {
                    "$addFields": {
                        "isBuy": {
                            "$and": [
                                {"$eq": ["$type", "BUY"]},
                                {
                                    "$not": [
                                        {
                                            "$in": [
                                                "$acq",
                                                [
                                                    "award_or_grant",
                                                    "gift",
                                                    "tax_withholding_or_exercise_cost",
                                                    "AWARD",
                                                    "GIFT",
                                                    "OPTION_EXERCISE",
                                                    "TAX_WITHHOLDING",
                                                ],
                                            ]
                                        }
                                    ]
                                },
                            ]
                        },
                        "isSell": {
                            "$and": [
                                {"$eq": ["$type", "SELL"]},
                                {
                                    "$not": [
                                        {
                                            "$in": [
                                                "$acq",
                                                [
                                                    "award_or_grant",
                                                    "gift",
                                                    "tax_withholding_or_exercise_cost",
                                                    "AWARD",
                                                    "GIFT",
                                                    "OPTION_EXERCISE",
                                                    "TAX_WITHHOLDING",
                                                ],
                                            ]
                                        }
                                    ]
                                },
                            ]
                        },
                    }
                },
                # Gruppierung nach Tag
                {
                    "$group": {
                        "_id": "$_id.date",
                        "buys": {"$sum": {"$cond": ["$isBuy", 1, 0]}},
                        "sells": {"$sum": {"$cond": ["$isSell", 1, 0]}},
                        "total": {"$sum": 1},
                    }
                },
                # Sortierung
                {"$sort": {"_id": 1}},
                # Finale Projektion
                {
                    "$project": {
                        "_id": 0,
                        "date": "$_id",
                        "buys": 1,
                        "sells": 1,
                        "total": 1,
                    }
                },
            ]

            result = await InsiderTrade.aggregate(pipeline, allowDiskUse=True).to_list()

            logger.debug(f"Fetched {len(result)} days of transaction data")
            return result

        except Exception as e:
            logger.error(f"Error fetching daily transaction data: {e}", exc_info=True)
            return []

    @classmethod
    def _fill_daily_data(
        cls,
        daily_data: list[dict[str, Any]],
        from_date: datetime,
        to_date: datetime,
    ) -> list[dict[str, Any]]:
        """
        Füllt fehlende Tage mit 0-Werten auf, um kontinuierliche Zeitreihen zu erstellen.
        """
        data_dict = {d["date"]: d for d in daily_data}
        filled = []
        current = from_date
        while current <= to_date:
            date_str = current.strftime("%Y-%m-%d")
            if date_str in data_dict:
                filled.append(data_dict[date_str])
            else:
                filled.append({"date": date_str, "buys": 0, "sells": 0, "total": 0})
            current += timedelta(days=1)
        return filled

    @classmethod
    def _calculate_indicator_series(
        cls,
        daily_data: list[dict[str, Any]],
        days: int,
    ) -> list[dict[str, Any]]:
        """
        Berechnet Insider-Indikator als Zeitreihe.

        Wert = (Anzahl Käufe / (Anzahl Käufe + Anzahl Verkäufe)) * 100
        mit 28-Tage gleitendem Fenster.
        """
        if not daily_data:
            return []

        # Sortiere nach Datum
        sorted_data = sorted(daily_data, key=lambda x: x["date"])

        # Berechne gleitenden Durchschnitt
        series = []
        window = cls.INDICATOR_WINDOW_DAYS

        for i in range(len(sorted_data)):
            # Fenster: i-window+1 bis i (inklusive)
            start_idx = max(0, i - window + 1)
            window_data = sorted_data[start_idx : i + 1]

            total_buys = sum(d["buys"] for d in window_data)
            total_sells = sum(d["sells"] for d in window_data)
            total_transactions = total_buys + total_sells

            if total_transactions > 0:
                indicator_value = (total_buys / total_transactions) * 100
            else:
                indicator_value = 50.0  # Neutral wenn keine Daten

            series.append(
                {
                    "date": sorted_data[i]["date"],
                    "value": round(indicator_value, 2),
                    "buys": total_buys,
                    "sells": total_sells,
                    "transactions": total_transactions,
                }
            )

        # Nur die letzten 'days' Tage zurückgeben
        return series[-days:] if len(series) > days else series

    @classmethod
    def _calculate_barometer_series(
        cls,
        daily_data: list[dict[str, Any]],
        days: int,
    ) -> list[dict[str, Any]]:
        """
        Berechnet Insiderkauf-Barometer als Zeitreihe.

        Zeigt Abweichung vom 12-Monats-Durchschnitt.
        Skaliert auf historischen Maximalausschlag.
        """
        if not daily_data:
            return []

        # Erst Indikator-Serie berechnen (für alle Daten)
        indicator_full = cls._calculate_indicator_series(daily_data, len(daily_data))

        if len(indicator_full) < cls.REFERENCE_PERIOD_DAYS:
            # Nicht genug Daten für 12-Monats-Durchschnitt
            return []

        series = []

        for i in range(len(indicator_full)):
            current_value = indicator_full[i]["value"]

            # 12-Monats-Durchschnitt berechnen (365 Tage zurück, exklusive aktueller Tag)
            lookback_start = max(0, i - cls.REFERENCE_PERIOD_DAYS)
            reference_data = indicator_full[lookback_start:i] if i > 0 else []

            if reference_data:
                avg_12m = sum(d["value"] for d in reference_data) / len(reference_data)
            else:
                # Keine vorherigen Daten verfügbar - neutral als Default
                avg_12m = 50.0

            # Abweichung vom Durchschnitt
            deviation = current_value - avg_12m

            series.append(
                {
                    "date": indicator_full[i]["date"],
                    "value": round(deviation, 2),
                    "currentIndicator": round(current_value, 2),
                    "average12m": round(avg_12m, 2),
                }
            )

        # Historischer Maximalausschlag für Skalierung
        if series:
            max_positive = max(s["value"] for s in series)
            max_negative = min(s["value"] for s in series)
            max_deviation = max(abs(max_positive), abs(max_negative))

            # Normalisiere auf -100 bis +100
            if max_deviation > 0:
                for s in series:
                    s["normalized"] = round((s["value"] / max_deviation) * 100, 2)
            else:
                for s in series:
                    s["normalized"] = 0

        # Nur die letzten 'days' Tage zurückgeben
        return series[-days:] if len(series) > days else series

    @classmethod
    def _calculate_activity_series(
        cls,
        daily_data: list[dict[str, Any]],
        days: int,
    ) -> list[dict[str, Any]]:
        """
        Berechnet Insider-Aktivitätsanzeige als Zeitreihe.

        Durchschnittliche Anzahl Transaktionen pro Tag im 28-Tage-Fenster.
        """
        if not daily_data:
            return []

        sorted_data = sorted(daily_data, key=lambda x: x["date"])
        series = []
        window = cls.INDICATOR_WINDOW_DAYS

        for i in range(len(sorted_data)):
            start_idx = max(0, i - window + 1)
            window_data = sorted_data[start_idx : i + 1]

            total_transactions = sum(d["total"] for d in window_data)
            avg_per_day = total_transactions / len(window_data) if window_data else 0

            series.append(
                {
                    "date": sorted_data[i]["date"],
                    "value": round(avg_per_day, 2),
                    "totalTransactions": total_transactions,
                    "windowDays": len(window_data),
                }
            )

        # 12-Monats-Durchschnitt für Normalisierung
        if len(series) >= cls.REFERENCE_PERIOD_DAYS:
            for i in range(len(series)):
                lookback_start = max(0, i - cls.REFERENCE_PERIOD_DAYS)
                reference_data = series[lookback_start:i] if i > 0 else []

                if reference_data:
                    avg_12m = sum(d["value"] for d in reference_data) / len(reference_data)
                else:
                    # Keine vorherigen Daten - aktuellen Wert als Referenz verwenden
                    avg_12m = series[i]["value"]

                series[i]["average12m"] = round(avg_12m, 2)

                # Abweichung vom Durchschnitt
                if avg_12m > 0:
                    deviation_pct = ((series[i]["value"] - avg_12m) / avg_12m) * 100
                    series[i]["deviationPercent"] = round(deviation_pct, 2)
                else:
                    series[i]["deviationPercent"] = 0

        # Historischer Max für Normalisierung
        if series:
            max_value = max(s["value"] for s in series)
            if max_value > 0:
                for s in series:
                    s["normalized"] = round((s["value"] / max_value) * 100, 2)

        # Nur die letzten 'days' Tage zurückgeben
        return series[-days:] if len(series) > days else series

    @classmethod
    def _get_current_values(cls, daily_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Berechnet aktuelle Sentiment-Werte (neuester Stand)."""
        if not daily_data:
            return {
                "insiderIndicator": {"value": 50.0, "interpretation": "neutral"},
                "insiderBarometer": {"value": 0.0, "normalized": 0.0, "average12m": 50.0, "interpretation": "neutral"},
                "activityIndicator": {"value": 0.0, "deviationPercent": 0.0, "interpretation": "low"},
            }

        # Berechne alle Serien
        indicator_series = cls._calculate_indicator_series(daily_data, cls.INDICATOR_WINDOW_DAYS)
        barometer_series = cls._calculate_barometer_series(daily_data, cls.INDICATOR_WINDOW_DAYS)
        activity_series = cls._calculate_activity_series(daily_data, cls.INDICATOR_WINDOW_DAYS)

        # Neueste Werte
        current_indicator = indicator_series[-1] if indicator_series else None
        current_barometer = barometer_series[-1] if barometer_series else None
        current_activity = activity_series[-1] if activity_series else None

        def interpret_indicator(value: float) -> str:
            if value >= 60:
                return "bullish"
            elif value >= 45:
                return "slightly_bullish"
            elif value >= 40:
                return "neutral"
            elif value >= 30:
                return "slightly_bearish"
            else:
                return "bearish"

        def interpret_barometer(normalized: float) -> str:
            if normalized >= 50:
                return "strong_bullish"
            elif normalized >= 20:
                return "bullish"
            elif normalized >= -20:
                return "neutral"
            elif normalized >= -50:
                return "bearish"
            else:
                return "strong_bearish"

        def interpret_activity(deviation_pct: float) -> str:
            if deviation_pct >= 50:
                return "very_high"
            elif deviation_pct >= 20:
                return "high"
            elif deviation_pct >= -20:
                return "normal"
            else:
                return "low"

        return {
            "insiderIndicator": {
                "value": current_indicator["value"] if current_indicator else 50.0,
                "buys": current_indicator["buys"] if current_indicator else 0,
                "sells": current_indicator["sells"] if current_indicator else 0,
                "transactions": current_indicator["transactions"] if current_indicator else 0,
                "interpretation": interpret_indicator(
                    current_indicator["value"] if current_indicator else 50.0
                ),
            },
            "insiderBarometer": {
                "value": current_barometer["value"] if current_barometer else 0.0,
                "normalized": current_barometer.get("normalized", 0.0) if current_barometer else 0.0,
                "average12m": current_barometer.get("average12m", 50.0) if current_barometer else 50.0,
                "interpretation": interpret_barometer(
                    current_barometer.get("normalized", 0.0) if current_barometer else 0.0
                ),
            },
            "activityIndicator": {
                "value": current_activity["value"] if current_activity else 0.0,
                "deviationPercent": (
                    current_activity.get("deviationPercent", 0.0) if current_activity else 0.0
                ),
                "interpretation": interpret_activity(
                    current_activity.get("deviationPercent", 0.0) if current_activity else 0.0
                ),
            },
        }

    @classmethod
    def _calculate_market_statistics(
        cls,
        daily_data: list[dict[str, Any]],
        days: int,
    ) -> dict[str, Any]:
        """Berechnet zusätzliche Markt-Statistiken für besseren Kontext."""
        if not daily_data:
            return {
                "totalTransactions": 0,
                "totalBuys": 0,
                "totalSells": 0,
                "avgDailyTransactions": 0.0,
                "buySellRatio": 1.0,
                "activeDays": 0,
                "daysWithoutActivity": 0,
                "dataQuality": "limited",
                "dataQualityScore": 0.0,
            }

        # Filtere auf die letzten 'days' Tage
        sorted_data = sorted(daily_data, key=lambda x: x["date"])
        recent_data = sorted_data[-days:] if len(sorted_data) > days else sorted_data

        total_buys = sum(d["buys"] for d in recent_data)
        total_sells = sum(d["sells"] for d in recent_data)
        total_transactions = sum(d["total"] for d in recent_data)

        active_days = len([d for d in recent_data if d["total"] > 0])
        days_without_activity = len(recent_data) - active_days

        avg_daily = total_transactions / len(recent_data) if recent_data else 0

        # Sichere Buy/Sell Ratio Berechnung
        if total_sells > 0:
            buy_sell_ratio = min(total_buys / total_sells, 999.99)
        elif total_buys > 0:
            buy_sell_ratio = 999.99
        else:
            buy_sell_ratio = 1.0

        # Datenqualität bewerten
        activity_ratio = active_days / len(recent_data) if recent_data else 0
        if activity_ratio > 0.7 and total_transactions > 50:
            data_quality = "excellent"
        elif activity_ratio > 0.5 and total_transactions > 20:
            data_quality = "good"
        elif activity_ratio > 0.3 or total_transactions > 10:
            data_quality = "moderate"
        else:
            data_quality = "limited"

        return {
            "totalTransactions": total_transactions,
            "totalBuys": total_buys,
            "totalSells": total_sells,
            "avgDailyTransactions": round(avg_daily, 2),
            "buySellRatio": round(buy_sell_ratio, 2),
            "activeDays": active_days,
            "daysWithoutActivity": days_without_activity,
            "dataQuality": data_quality,
            "dataQualityScore": round(activity_ratio * 100, 1),
        }

    @staticmethod
    def _interpret_value(value: float) -> str:
        """Interpretiert einen Indikator-Wert."""
        if value >= 60:
            return "bullish"
        elif value >= 45:
            return "slightly_bullish"
        elif value >= 40:
            return "neutral"
        elif value >= 30:
            return "slightly_bearish"
        else:
            return "bearish"

    @staticmethod
    def _interpret_momentum(momentum: dict[str, float]) -> str:
        """Interpretiert Momentum-Daten."""
        if not momentum:
            return "neutral"

        short_term = momentum.get("shortTerm", 0)
        medium_term = momentum.get("mediumTerm", 0)

        if short_term > 5 and medium_term > 0:
            return "accelerating_bullish"
        elif short_term > 0 and medium_term > 0:
            return "bullish"
        elif short_term < -5 and medium_term < 0:
            return "accelerating_bearish"
        elif short_term < 0 and medium_term < 0:
            return "bearish"
        else:
            return "mixed"
