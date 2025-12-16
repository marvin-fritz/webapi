"""Pydantic schemas for Sentiment Analysis."""

from datetime import datetime

from pydantic import BaseModel, Field


# --- Time Series Data Points ---

class IndicatorDataPoint(BaseModel):
    """Data point for insider indicator time series."""
    
    date: str
    value: float
    buys: int
    sells: int
    transactions: int


class BarometerDataPoint(BaseModel):
    """Data point for insider barometer time series."""
    
    date: str
    value: float
    currentIndicator: float
    average12m: float
    normalized: float = 0.0


class ActivityDataPoint(BaseModel):
    """Data point for activity indicator time series."""
    
    date: str
    value: float
    totalTransactions: int
    windowDays: int
    average12m: float | None = None
    deviationPercent: float | None = None
    normalized: float | None = None


# --- Current Values ---

class InsiderIndicatorCurrent(BaseModel):
    """Current insider indicator value."""
    
    value: float
    buys: int = 0
    sells: int = 0
    transactions: int = 0
    interpretation: str


class InsiderBarometerCurrent(BaseModel):
    """Current insider barometer value."""
    
    value: float
    normalized: float
    average12m: float
    interpretation: str


class ActivityIndicatorCurrent(BaseModel):
    """Current activity indicator value."""
    
    value: float
    deviationPercent: float
    interpretation: str


class CurrentSentiment(BaseModel):
    """Current sentiment values."""
    
    insiderIndicator: InsiderIndicatorCurrent
    insiderBarometer: InsiderBarometerCurrent
    activityIndicator: ActivityIndicatorCurrent


# --- Time Series Container ---

class SentimentTimeSeries(BaseModel):
    """Container for sentiment time series data."""
    
    insiderIndicator: list[IndicatorDataPoint]
    insiderBarometer: list[BarometerDataPoint]
    activityIndicator: list[ActivityDataPoint]


# --- Market Statistics ---

class MarketStatistics(BaseModel):
    """Market statistics for sentiment analysis."""
    
    totalTransactions: int
    totalBuys: int
    totalSells: int
    avgDailyTransactions: float
    buySellRatio: float
    activeDays: int
    daysWithoutActivity: int
    dataQuality: str
    dataQualityScore: float


# --- Metadata ---

class TimeRange(BaseModel):
    """Time range metadata."""
    
    days: int
    fromDate: str = Field(..., alias="from")
    toDate: str = Field(..., alias="to")
    
    class Config:
        populate_by_name = True


class SentimentParameters(BaseModel):
    """Sentiment calculation parameters."""
    
    indicatorWindow: int
    referencePeriod: int


class SentimentMetadata(BaseModel):
    """Metadata for sentiment response."""
    
    generatedAt: str
    timeRange: TimeRange
    jurisdiction: str
    parameters: SentimentParameters
    dataPoints: int


class CurrentSentimentMetadata(BaseModel):
    """Metadata for current sentiment response."""
    
    generatedAt: str
    jurisdiction: str


# --- Main Response Schemas ---

class SentimentResponse(BaseModel):
    """Full sentiment analysis response."""
    
    metadata: SentimentMetadata
    current: CurrentSentiment
    timeSeries: SentimentTimeSeries
    marketStatistics: MarketStatistics


class CurrentSentimentResponse(BaseModel):
    """Current sentiment response (no history)."""
    
    metadata: CurrentSentimentMetadata
    current: CurrentSentiment


# --- Market Breadth Schemas ---

class BreadthMetrics(BaseModel):
    """Market breadth metrics."""
    
    totalActiveCompanies: int
    bullishCompanies: int
    bearishCompanies: int
    neutralCompanies: int
    breadthRatio: float


class JurisdictionBreakdown(BaseModel):
    """Jurisdiction breakdown for market breadth."""
    
    jurisdiction: str
    transactions: int
    buys: int
    sells: int
    buyRatio: float


class TopActiveCompany(BaseModel):
    """Top active company in market breadth."""
    
    isin: str
    companyName: str
    jurisdiction: str
    transactions: int
    buys: int
    sells: int
    buyRatio: float
    sentiment: str
    lastActivity: str | None = None


class MarketBreadthMetadata(BaseModel):
    """Metadata for market breadth response."""
    
    generatedAt: str
    days: int
    jurisdiction: str


class MarketBreadthResponse(BaseModel):
    """Market breadth analysis response."""
    
    metadata: MarketBreadthMetadata
    breadthMetrics: BreadthMetrics
    jurisdictionBreakdown: list[JurisdictionBreakdown]
    topActiveCompanies: list[TopActiveCompany]


# --- Top Movers Schemas ---

class TopMover(BaseModel):
    """Top mover company."""
    
    isin: str
    companyName: str
    jurisdiction: str
    transactions: int
    buys: int
    sells: int
    buyRatio: float
    uniqueInsiders: int
    activityScore: float
    sentiment: str
    lastActivity: str | None = None


class TopMoversMetadata(BaseModel):
    """Metadata for top movers response."""
    
    generatedAt: str
    days: int
    limit: int
    minTransactions: int
    jurisdiction: str
    resultCount: int


class TopMoversResponse(BaseModel):
    """Top movers response."""
    
    metadata: TopMoversMetadata
    topMovers: list[TopMover]


# --- Trends Schemas ---

class TrendWindow(BaseModel):
    """Trend data for a specific time window."""
    
    avgIndicator: float
    recentBuys: int
    recentSells: int
    sentiment: str


class Momentum(BaseModel):
    """Momentum indicators."""
    
    shortTerm: float | None = None
    mediumTerm: float | None = None
    longTerm: float | None = None


class TrendsMetadata(BaseModel):
    """Metadata for trends response."""
    
    generatedAt: str
    jurisdiction: str


class TrendsResponse(BaseModel):
    """Trend analysis response."""
    
    metadata: TrendsMetadata
    trends: dict[str, TrendWindow]
    momentum: Momentum
    interpretation: str
