"""API v1 router aggregating all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import dashboard, health, insider_trades, news, news_sources, search, sec_financials, sentiment, stocks, ticker

api_router = APIRouter(prefix="/api/v1")

# Include endpoint routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(news_sources.router, prefix="/news-sources", tags=["News Sources"])
api_router.include_router(news.router, prefix="/news", tags=["News"])
api_router.include_router(insider_trades.router, prefix="/insider-trades", tags=["Insider Trades"])
api_router.include_router(ticker.router, prefix="/ticker", tags=["Ticker Signals"])
api_router.include_router(sec_financials.router, prefix="/sec-financials", tags=["SEC Financials"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["Stock Index"])
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["Sentiment Analysis"])
