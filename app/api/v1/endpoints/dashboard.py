"""REST API endpoints for Dashboard Statistics."""

import logging
import traceback

from fastapi import APIRouter, HTTPException, Query

from app.schemas.dashboard import DashboardStatsResponse, QuickStatsResponse
from app.services.dashboard import DashboardService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    hours: int = Query(
        24,
        ge=1,
        le=336,
        description="Zeitraum in Stunden (1-336, max 2 Wochen)",
    ),
    timezone: str = Query(
        "Europe/Berlin",
        description="Zeitzone für Zeitreihen-Aggregation",
    ),
    extended: bool = Query(
        True,
        description="Erweiterte Statistiken einschließen",
    ),
    debug: bool = Query(
        False,
        description="Debug-Modus für Fehlerdetails",
    ),
) -> DashboardStatsResponse:
    """
    Vollständige Dashboard-Statistiken abrufen.
    
    Liefert aggregierte Statistiken über Insider-Trading-Aktivitäten:
    
    - **Echtzeit-Statistiken**: Neue Trades, Käufe/Verkäufe-Verhältnis
    - **Aktivitäts-Monitoring**: Verarbeitete Aktien, stündliche Aktivität
    - **Top-Performer**: Meistgehandelte Aktien nach Insider-Aktivität
    - **Volumen-Analyse**: Handelsvolumen nach Währung
    
    **Empfohlene Refresh-Intervalle:**
    - 1-24 Stunden: 60 Sekunden
    - 24-72 Stunden: 5 Minuten
    - 72+ Stunden: Manuell
    
    Returns:
        DashboardStatsResponse mit allen Statistiken
    """
    try:
        stats = await DashboardService.get_dashboard_stats(
            hours=hours,
            tz=timezone,
            include_extended=extended,
        )
        return stats
    except Exception as e:
        logger.error(f"Error in dashboard stats endpoint: {e}", exc_info=True)
        if debug:
            raise HTTPException(status_code=500, detail=f"Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/quick", response_model=QuickStatsResponse)
async def get_quick_stats(
    hours: int = Query(
        24,
        ge=1,
        le=168,
        description="Zeitraum in Stunden (1-168)",
    ),
) -> QuickStatsResponse:
    """
    Schnelle Statistiken für Dashboard-Widgets.
    
    Lightweight Endpoint für schnelle Aktualisierungen ohne
    die vollständigen Details. Ideal für:
    
    - KPI-Widgets
    - Statusanzeigen
    - Schnelle Trend-Checks
    
    Enthält:
    - Gesamtanzahl Trades
    - Käufe/Verkäufe
    - Top-Ticker
    - Trend-Richtung (up/down/neutral)
    
    Returns:
        QuickStatsResponse mit Key-Metrics
    """
    try:
        stats = await DashboardService.get_quick_stats(hours=hours)
        return stats
    except Exception as e:
        logger.error(f"Error in quick stats endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def dashboard_health() -> dict:
    """
    Health Check für Dashboard-Service.
    
    Prüft die Verfügbarkeit des Dashboard-Services.
    """
    return {
        "status": "healthy",
        "service": "dashboard",
    }
