"""Pydantic schemas for Dashboard Statistics."""

from datetime import datetime

from pydantic import BaseModel, Field


# === Time Range ===

class TimeRange(BaseModel):
    """Time range metadata for the dashboard response."""
    
    fromDate: str = Field(..., alias="from", description="ISO-Datum Start")
    toDate: str = Field(..., alias="to", description="ISO-Datum Ende")
    timezone: str = Field(default="Europe/Berlin", description="Zeitzone")
    hours: int = Field(..., description="Angefragter Zeitraum in Stunden")
    
    class Config:
        populate_by_name = True


# === Processing Statistics ===

class ProcessedPerHour(BaseModel):
    """Hourly processing statistics."""
    
    hour: str = Field(..., description="ISO-Datum der Stunde")
    count: int = Field(default=0, description="Anzahl verarbeiteter Aktien in dieser Stunde")
    tradesCount: int = Field(default=0, description="Anzahl neuer Trades in dieser Stunde")


class ProcessingStats(BaseModel):
    """Processing statistics for the time range."""
    
    processedStocks: int = Field(default=0, description="Anzahl eindeutiger Aktien mit Insider-Aktivität")
    totalTrades: int = Field(default=0, description="Gesamtanzahl aller Trades im Zeitraum")
    processedPerHour: list[ProcessedPerHour] = Field(
        default_factory=list,
        description="Stündliche Aufschlüsselung"
    )


# === Insider Trades Statistics ===

class TradesByType(BaseModel):
    """Trade counts by transaction type."""
    
    BUY: int = Field(default=0, description="Anzahl Insider-Käufe")
    SELL: int = Field(default=0, description="Anzahl Insider-Verkäufe")


class TopTicker(BaseModel):
    """Top traded ticker information."""
    
    ticker: str = Field(..., description="Ticker-Symbol")
    companyName: str | None = Field(default=None, description="Firmenname")
    count: int = Field(..., description="Anzahl Trades")
    isin: str | None = Field(default=None, description="ISIN")
    jurisdiction: str | None = Field(default=None, description="Jurisdiktion")


class VolumeByCurrency(BaseModel):
    """Volume aggregated by currency."""
    
    currency: str = Field(..., description="Währungscode (EUR, USD, CHF, etc.)")
    totalVolume: float = Field(default=0.0, description="Gesamtvolumen in dieser Währung")
    avgVolume: float = Field(default=0.0, description="Durchschnittliches Volumen pro Trade")
    count: int = Field(default=0, description="Anzahl Trades in dieser Währung")


class InsiderTradesStats(BaseModel):
    """Insider trades statistics."""
    
    newTrades: int = Field(default=0, description="Anzahl neuer Trades im Zeitraum")
    byType: TradesByType = Field(default_factory=TradesByType, description="Aufschlüsselung nach Transaktionstyp")
    topTickersByCount: list[TopTicker] = Field(
        default_factory=list,
        description="Top Aktien nach Trade-Anzahl (max 20)"
    )
    volumeByCurrency: list[VolumeByCurrency] = Field(
        default_factory=list,
        description="Volumen aggregiert nach Währung"
    )


# === Additional Statistics (Extended) ===

class JurisdictionStats(BaseModel):
    """Statistics by jurisdiction."""
    
    jurisdiction: str = Field(..., description="Ländercode (US, DE, GB, etc.)")
    trades: int = Field(default=0, description="Anzahl Trades")
    buys: int = Field(default=0, description="Anzahl Käufe")
    sells: int = Field(default=0, description="Anzahl Verkäufe")
    buyRatio: float = Field(default=50.0, description="Kaufanteil in Prozent")


class TopInsider(BaseModel):
    """Top insider by activity."""
    
    insiderName: str = Field(..., description="Name des Insiders")
    companyName: str | None = Field(default=None, description="Primäre Firma")
    transactions: int = Field(default=0, description="Anzahl Transaktionen")
    buys: int = Field(default=0, description="Anzahl Käufe")
    sells: int = Field(default=0, description="Anzahl Verkäufe")
    totalVolume: float = Field(default=0.0, description="Gesamtvolumen")


class ExtendedStats(BaseModel):
    """Extended statistics for the dashboard."""
    
    byJurisdiction: list[JurisdictionStats] = Field(
        default_factory=list,
        description="Aufschlüsselung nach Jurisdiktion"
    )
    topInsiders: list[TopInsider] = Field(
        default_factory=list,
        description="Top Insider nach Aktivität"
    )
    avgTradesPerStock: float = Field(default=0.0, description="Durchschnittliche Trades pro Aktie")
    buyPercentage: float = Field(default=50.0, description="Kaufanteil in Prozent")
    mostActiveHour: str | None = Field(default=None, description="Stunde mit meisten Trades")
    mostActiveHourCount: int = Field(default=0, description="Trades in der aktivsten Stunde")


# === Main Response ===

class DashboardStatsResponse(BaseModel):
    """Full dashboard statistics response."""
    
    timeRange: TimeRange = Field(..., description="Metadata über den Zeitraum")
    processing: ProcessingStats = Field(..., description="Verarbeitungs-Statistiken")
    insiderTrades: InsiderTradesStats = Field(..., description="Insider-Trading-Statistiken")
    extended: ExtendedStats | None = Field(default=None, description="Erweiterte Statistiken")


# === Quick Stats Response (Lightweight) ===

class QuickStatsResponse(BaseModel):
    """Lightweight quick stats for dashboard widgets."""
    
    generatedAt: str = Field(..., description="ISO-Datum der Generierung")
    hours: int = Field(..., description="Zeitraum in Stunden")
    
    # Key metrics
    totalTrades: int = Field(default=0)
    processedStocks: int = Field(default=0)
    buys: int = Field(default=0)
    sells: int = Field(default=0)
    buyPercentage: float = Field(default=50.0)
    
    # Top performer
    topTicker: str | None = Field(default=None)
    topTickerCount: int = Field(default=0)
    
    # Trend indicator
    trendDirection: str = Field(default="neutral", description="up, down, or neutral")
