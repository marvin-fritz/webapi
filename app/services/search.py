"""Service for unified Search functionality."""

import logging
from typing import Any

from app.models.news import News
from app.models.stock_index import StockIndex
from app.schemas.search import (
    BaseSearchResult,
    NewsSearchResult,
    SearchResultAction,
    SearchResultType,
    StockSearchResult,
)

logger = logging.getLogger(__name__)


class SearchService:
    """Service class for unified search across multiple collections."""
    
    # Base URLs for redirects
    STOCK_DETAIL_URL = "https://finanz-copilot.de/stock/{isin}"
    NEWS_DETAIL_URL = "{link}"  # Direct link to news article
    
    @classmethod
    async def search(
        cls,
        query: str,
        types: list[SearchResultType] | None = None,
        limit: int = 10,
    ) -> list[BaseSearchResult]:
        """
        Perform unified search across multiple collections.
        
        Args:
            query: Search query string
            types: Optional list of result types to filter by
            limit: Maximum results per type
            
        Returns:
            List of search results sorted by relevance
        """
        results: list[BaseSearchResult] = []
        
        # If no types specified, search all
        if types is None:
            types = [SearchResultType.STOCK, SearchResultType.NEWS]
        
        # Search stocks
        if SearchResultType.STOCK in types:
            stock_results = await cls._search_stocks(query, limit)
            results.extend(stock_results)
        
        # Search news
        if SearchResultType.NEWS in types:
            news_results = await cls._search_news(query, limit)
            results.extend(news_results)
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x.relevanceScore, reverse=True)
        
        return results
    
    @classmethod
    async def _search_stocks(
        cls,
        query: str,
        limit: int,
    ) -> list[StockSearchResult]:
        """Search in stockIndex collection."""
        try:
            # Search by name, ticker, or ISIN
            stocks = await StockIndex.find({
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"ticker": {"$regex": f"^{query}", "$options": "i"}},
                    {"isin": {"$regex": f"^{query}", "$options": "i"}},
                ]
            }).limit(limit).to_list()
            
            results = []
            for stock in stocks:
                # Calculate relevance score
                score = cls._calculate_stock_relevance(stock, query)
                
                # Build redirect URL
                isin = stock.isin or (stock.identifiers.isin if stock.identifiers else None)
                redirect_url = cls.STOCK_DETAIL_URL.format(isin=isin) if isin else "#"
                
                results.append(StockSearchResult(
                    id=str(stock.id),
                    type=SearchResultType.STOCK,
                    title=stock.name,
                    subtitle=f"{stock.ticker} • {stock.exchangeCode}",
                    description=f"{stock.securityType} • {stock.marketSector}",
                    ticker=stock.ticker,
                    isin=isin,
                    exchangeCode=stock.exchangeCode,
                    action=SearchResultAction(
                        type="redirect",
                        url=redirect_url,
                    ),
                    relevanceScore=score,
                    metadata={
                        "securityType": stock.securityType,
                        "marketSector": stock.marketSector,
                    },
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching stocks: {e}", exc_info=True)
            return []
    
    @classmethod
    async def _search_news(
        cls,
        query: str,
        limit: int,
    ) -> list[NewsSearchResult]:
        """Search in news collection."""
        try:
            # Search by title or description
            news_items = await News.find({
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                ]
            }).sort("-pubDate").limit(limit).to_list()
            
            results = []
            for news in news_items:
                # Calculate relevance score
                score = cls._calculate_news_relevance(news, query)
                
                results.append(NewsSearchResult(
                    id=str(news.id),
                    type=SearchResultType.NEWS,
                    title=news.title,
                    subtitle=f"{news.sourceName} • {news.category}",
                    description=news.description[:200] if news.description else None,
                    image=news.image,
                    source=news.sourceName,
                    category=news.category,
                    pubDate=news.pubDate,
                    action=SearchResultAction(
                        type="redirect",
                        url=news.link,  # Direct link to original article
                    ),
                    relevanceScore=score,
                    metadata={
                        "category": news.category,
                        "sourceName": news.sourceName,
                    },
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching news: {e}", exc_info=True)
            return []
    
    @staticmethod
    def _calculate_stock_relevance(stock: StockIndex, query: str) -> float:
        """
        Calculate relevance score for a stock result.
        Higher score = more relevant.
        """
        query_lower = query.lower()
        score = 0.0
        
        # Exact ticker match (highest priority)
        if stock.ticker and stock.ticker.lower() == query_lower:
            score += 100.0
        # Ticker starts with query
        elif stock.ticker and stock.ticker.lower().startswith(query_lower):
            score += 80.0
        
        # ISIN match
        isin = stock.isin or (stock.identifiers.isin if stock.identifiers else None)
        if isin and isin.lower().startswith(query_lower):
            score += 90.0
        
        # Name exact match
        if stock.name and stock.name.lower() == query_lower:
            score += 70.0
        # Name starts with query
        elif stock.name and stock.name.lower().startswith(query_lower):
            score += 50.0
        # Name contains query
        elif stock.name and query_lower in stock.name.lower():
            score += 30.0
        
        return score
    
    @staticmethod
    def _calculate_news_relevance(news: News, query: str) -> float:
        """
        Calculate relevance score for a news result.
        Higher score = more relevant.
        """
        query_lower = query.lower()
        score = 0.0
        
        # Title exact match
        if news.title and news.title.lower() == query_lower:
            score += 80.0
        # Title starts with query
        elif news.title and news.title.lower().startswith(query_lower):
            score += 60.0
        # Title contains query
        elif news.title and query_lower in news.title.lower():
            score += 40.0
        
        # Description contains query
        if news.description and query_lower in news.description.lower():
            score += 20.0
        
        # Recency bonus (newer = slightly higher score)
        # Max 10 points for articles from today, decreasing over time
        from datetime import datetime, timezone
        if news.pubDate:
            # Handle both offset-naive and offset-aware datetimes
            pub_date = news.pubDate
            if pub_date.tzinfo is None:
                # If pubDate is offset-naive, assume UTC
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            days_old = (datetime.now(timezone.utc) - pub_date).days
            recency_bonus = max(0, 10 - days_old)
            score += recency_bonus
        
        return score
