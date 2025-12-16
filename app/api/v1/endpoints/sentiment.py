"""REST API endpoints for Sentiment Analysis."""

import logging

from fastapi import APIRouter, HTTPException, Query

from app.services.sentiment import SentimentService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
async def get_sentiment(
    days: int = Query(90, ge=1, le=730, description="Anzahl Tage für Historie (max: 730)"),
    jurisdiction: str | None = Query(None, description="Filter nach Jurisdiktion (z.B. 'US', 'DE')"),
):
    """
    Vollständige Sentiment-Analyse mit Historie.

    Berechnet verschiedene Sentiment-Indikatoren basierend auf Insider-Trading-Aktivitäten:
    - Insider-Indikator: Anteil Käufe an Gesamt-Transaktionen (28-Tage gleitend)
    - Insiderkauf-Barometer: Abweichung vom 12-Monats-Durchschnitt
    - Insider-Aktivitätsanzeige: Durchschnittliche Transaktionen pro Tag

    Returns:
        JSON mit Sentiment-Daten für Graphen inkl. Zeitreihen und aktuelle Werte
    """
    try:
        sentiment_data = await SentimentService.calculate_sentiment(days, jurisdiction)
        return sentiment_data
    except Exception as e:
        logger.error(f"Error in sentiment endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/current")
async def get_current_sentiment(
    jurisdiction: str | None = Query(None, description="Filter nach Jurisdiktion (z.B. 'US', 'DE')"),
):
    """
    Aktuelle Sentiment-Werte (ohne Historie).

    Schneller Endpoint für Dashboard-Anzeigen mit nur den aktuellen Werten
    ohne die vollständige Zeitreihen-Historie.

    Returns:
        JSON mit aktuellen Sentiment-Werten
    """
    try:
        current_data = await SentimentService.get_current_sentiment(jurisdiction)
        return current_data
    except Exception as e:
        logger.error(f"Error in current sentiment endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/market-breadth")
async def get_market_breadth(
    days: int = Query(30, ge=1, le=365, description="Anzahl Tage für Analyse"),
    jurisdiction: str | None = Query(None, description="Filter nach Jurisdiktion"),
):
    """
    Marktbreite-Analyse: Zeigt Verteilung über verschiedene Dimensionen.

    Returns:
        JSON mit Marktbreite-Metriken:
        - Jurisdiktion-Verteilung
        - Top aktive ISINs
        - Buy/Sell-Ratio nach Volumen
        - Aktivitäts-Trends
    """
    try:
        breadth_data = await SentimentService.calculate_market_breadth(days, jurisdiction)
        return breadth_data
    except Exception as e:
        logger.error(f"Error in market breadth endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/top-movers")
async def get_top_movers(
    days: int = Query(7, ge=1, le=90, description="Zeitraum in Tagen"),
    limit: int = Query(20, ge=1, le=100, description="Anzahl Ergebnisse"),
    jurisdiction: str | None = Query(None, description="Filter nach Jurisdiktion"),
    minTransactions: int = Query(3, ge=1, description="Mindestanzahl Transaktionen"),
):
    """
    Top-Mover: ISINs mit höchster Insider-Aktivität.

    Identifiziert die aktivsten Unternehmen basierend auf Insider-Trading-Aktivität
    und berechnet für jedes einen Sentiment-Score.

    Returns:
        Liste der aktivsten ISINs mit Sentiment-Scores
    """
    try:
        movers_data = await SentimentService.get_top_movers(
            days, limit, jurisdiction, minTransactions
        )
        return movers_data
    except Exception as e:
        logger.error(f"Error in top movers endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trends")
async def get_trends(
    jurisdiction: str | None = Query(None, description="Filter nach Jurisdiktion"),
):
    """
    Trend-Analyse: Kurzfrist vs. Langfrist Momentum.

    Vergleicht Sentiment über verschiedene Zeitfenster (7T, 28T, 90T, 365T)
    und berechnet Momentum-Indikatoren.

    Returns:
        JSON mit Trend-Vergleich und Momentum-Analyse
    """
    try:
        trends_data = await SentimentService.calculate_trends(jurisdiction)
        return trends_data
    except Exception as e:
        logger.error(f"Error in trends endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
