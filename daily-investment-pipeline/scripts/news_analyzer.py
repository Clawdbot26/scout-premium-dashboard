#!/usr/bin/env python3
"""
News Analysis System
Automated news scraping and analysis for key investment sectors
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from urllib.parse import quote
import time
import re

# Add parent directory to path for config imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.settings import get_config

@dataclass
class NewsArticle:
    title: str
    url: str
    source: str
    published_at: str
    summary: str
    sentiment: str
    relevance_score: float
    tickers_mentioned: List[str]
    sector: str
    impact_level: str  # high, medium, low

class NewsAnalyzer:
    def __init__(self):
        self.config = get_config()
        self.sector_config = self.config['sectors'].FOCUS_SECTORS
        self.news_config = self.config['news']
        self.api_key = os.getenv('NEWS_API_KEY', '')
        
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of news text"""
        text_lower = text.lower()
        
        bullish_score = sum(1 for word in self.news_config.SENTIMENT_KEYWORDS['bullish'] 
                           if word in text_lower)
        bearish_score = sum(1 for word in self.news_config.SENTIMENT_KEYWORDS['bearish'] 
                           if word in text_lower)
        
        if bullish_score > bearish_score:
            return "bullish"
        elif bearish_score > bullish_score:
            return "bearish"
        else:
            return "neutral"
    
    def extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from text"""
        # Look for patterns like $NVDA, NVDA, or common ticker formats
        ticker_pattern = r'\b[A-Z]{2,5}\b'
        potential_tickers = re.findall(ticker_pattern, text)
        
        # Filter against known tickers from all sectors
        known_tickers = []
        for sector_data in self.sector_config.values():
            known_tickers.extend(sector_data['tickers'])
        
        return [ticker for ticker in potential_tickers if ticker in known_tickers]
    
    def calculate_relevance(self, article: Dict, sector: str) -> float:
        """Calculate relevance score for article to specific sector"""
        score = 0.0
        sector_keywords = self.sector_config[sector]['keywords']
        title_text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        # Keyword matching (0-50 points)
        keyword_matches = sum(1 for keyword in sector_keywords if keyword.lower() in title_text)
        score += min(keyword_matches * 10, 50)
        
        # Ticker mentions (0-30 points)
        tickers = self.extract_tickers(title_text.upper())
        sector_tickers = self.sector_config[sector]['tickers']
        ticker_matches = len([t for t in tickers if t in sector_tickers])
        score += min(ticker_matches * 15, 30)
        
        # Priority terms (0-20 points)
        priority_matches = sum(1 for term in self.news_config.PRIORITY_TERMS 
                             if term.lower() in title_text)
        score += min(priority_matches * 10, 20)
        
        return min(score, 100)  # Cap at 100
    
    def determine_impact_level(self, article: Dict, relevance_score: float) -> str:
        """Determine impact level based on relevance and content"""
        title_text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        high_impact_terms = ['earnings', 'acquisition', 'fda approval', 'breakthrough', 'guidance']
        high_impact_found = any(term in title_text for term in high_impact_terms)
        
        if relevance_score >= 80 or high_impact_found:
            return "high"
        elif relevance_score >= 50:
            return "medium"
        else:
            return "low"
    
    def classify_sector(self, article: Dict) -> str:
        """Determine which sector this article belongs to"""
        title_text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        sector_scores = {}
        for sector, sector_data in self.sector_config.items():
            score = 0
            for keyword in sector_data['keywords']:
                if keyword.lower() in title_text:
                    score += 1
            sector_scores[sector] = score
        
        if max(sector_scores.values()) == 0:
            return "general"
        
        return max(sector_scores, key=sector_scores.get)
    
    def fetch_news_articles(self, days_back: int = 1) -> List[Dict]:
        """Fetch news articles from various sources"""
        articles = []
        
        # Free sources (no API key required)
        articles.extend(self._fetch_yahoo_finance_news())
        articles.extend(self._fetch_reuters_rss())
        
        # Paid API sources (if API key available)
        if self.api_key:
            articles.extend(self._fetch_newsapi_articles(days_back))
        
        return articles
    
    def _fetch_yahoo_finance_news(self) -> List[Dict]:
        """Fetch news from Yahoo Finance (free)"""
        articles = []
        
        # Get news for each sector's top tickers
        for sector, sector_data in self.sector_config.items():
            for ticker in sector_data['tickers'][:3]:  # Limit to top 3 per sector
                try:
                    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        # This is a simplified version - Yahoo's actual news API is more complex
                        # In production, you'd use the yfinance library or scrape news sections
                        print(f"Fetched Yahoo Finance data for {ticker}")
                        time.sleep(0.5)  # Rate limiting
                        
                except Exception as e:
                    print(f"Error fetching Yahoo Finance news for {ticker}: {e}")
        
        return articles
    
    def _fetch_reuters_rss(self) -> List[Dict]:
        """Fetch news from Reuters RSS feeds (free)"""
        articles = []
        rss_feeds = [
            "https://feeds.reuters.com/reuters/businessNews",
            "https://feeds.reuters.com/reuters/technologyNews"
        ]
        
        for feed_url in rss_feeds:
            try:
                # In production, you'd parse RSS XML
                # For demo, we'll simulate
                print(f"Fetching RSS from {feed_url}")
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching RSS from {feed_url}: {e}")
        
        return articles
    
    def _fetch_newsapi_articles(self, days_back: int) -> List[Dict]:
        """Fetch articles from NewsAPI (requires API key)"""
        articles = []
        
        if not self.api_key:
            return articles
        
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Create search queries for each sector
        for sector, sector_data in self.sector_config.items():
            keywords = ' OR '.join(sector_data['keywords'][:5])  # Limit keywords
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'apiKey': self.api_key,
                'q': keywords,
                'from': from_date,
                'sortBy': 'relevancy',
                'language': 'en',
                'pageSize': 20
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles.extend(data.get('articles', []))
                    time.sleep(1)  # Rate limiting
                else:
                    print(f"NewsAPI error: {response.status_code}")
                    
            except Exception as e:
                print(f"Error fetching NewsAPI articles for {sector}: {e}")
        
        return articles
    
    def analyze_articles(self, articles: List[Dict]) -> List[NewsArticle]:
        """Analyze fetched articles and return structured data"""
        analyzed_articles = []
        
        for article in articles:
            try:
                # Skip articles without title or description
                if not article.get('title') or not article.get('description'):
                    continue
                
                sector = self.classify_sector(article)
                relevance_score = self.calculate_relevance(article, sector)
                
                # Skip low-relevance articles
                if relevance_score < 20:
                    continue
                
                analyzed_article = NewsArticle(
                    title=article.get('title', ''),
                    url=article.get('url', ''),
                    source=article.get('source', {}).get('name', 'Unknown'),
                    published_at=article.get('publishedAt', ''),
                    summary=article.get('description', '')[:200] + "...",
                    sentiment=self.analyze_sentiment(f"{article.get('title')} {article.get('description')}"),
                    relevance_score=relevance_score,
                    tickers_mentioned=self.extract_tickers(f"{article.get('title')} {article.get('description')}"),
                    sector=sector,
                    impact_level=self.determine_impact_level(article, relevance_score)
                )
                
                analyzed_articles.append(analyzed_article)
                
            except Exception as e:
                print(f"Error analyzing article: {e}")
                continue
        
        # Sort by relevance score (highest first)
        analyzed_articles.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return analyzed_articles
    
    def save_analysis(self, articles: List[NewsArticle], output_dir: str = "news-analysis"):
        """Save analyzed articles to JSON file"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{output_dir}/news_analysis_{timestamp}.json"
        
        # Convert to dict for JSON serialization
        articles_data = [asdict(article) for article in articles]
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'total_articles': len(articles_data),
            'articles': articles_data,
            'sector_summary': self._generate_sector_summary(articles)
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"News analysis saved to: {filename}")
        return filename
    
    def _generate_sector_summary(self, articles: List[NewsArticle]) -> Dict:
        """Generate summary statistics by sector"""
        summary = {}
        
        for sector in self.sector_config.keys():
            sector_articles = [a for a in articles if a.sector == sector]
            
            if sector_articles:
                summary[sector] = {
                    'article_count': len(sector_articles),
                    'avg_sentiment': self._calculate_avg_sentiment(sector_articles),
                    'high_impact_count': len([a for a in sector_articles if a.impact_level == 'high']),
                    'top_tickers': list(set([ticker for article in sector_articles 
                                           for ticker in article.tickers_mentioned]))[:5]
                }
        
        return summary
    
    def _calculate_avg_sentiment(self, articles: List[NewsArticle]) -> str:
        """Calculate average sentiment for a group of articles"""
        if not articles:
            return "neutral"
        
        sentiment_scores = {'bullish': 1, 'neutral': 0, 'bearish': -1}
        total_score = sum(sentiment_scores[article.sentiment] for article in articles)
        avg_score = total_score / len(articles)
        
        if avg_score > 0.3:
            return "bullish"
        elif avg_score < -0.3:
            return "bearish"
        else:
            return "neutral"

def main():
    """Main execution function"""
    print("🔍 Starting News Analysis System...")
    
    analyzer = NewsAnalyzer()
    
    # Fetch and analyze news
    print("📰 Fetching news articles...")
    raw_articles = analyzer.fetch_news_articles(days_back=1)
    
    print(f"📊 Analyzing {len(raw_articles)} articles...")
    analyzed_articles = analyzer.analyze_articles(raw_articles)
    
    # Save results
    output_file = analyzer.save_analysis(analyzed_articles)
    
    # Print summary
    print(f"\n✅ Analysis Complete!")
    print(f"📄 Total articles analyzed: {len(analyzed_articles)}")
    print(f"💾 Results saved to: {output_file}")
    
    # Show top articles
    print(f"\n🔥 Top 5 High-Impact Articles:")
    for i, article in enumerate(analyzed_articles[:5], 1):
        print(f"{i}. [{article.sector.upper()}] {article.title}")
        print(f"   Sentiment: {article.sentiment} | Relevance: {article.relevance_score:.1f}/100")
        print(f"   Tickers: {', '.join(article.tickers_mentioned) if article.tickers_mentioned else 'None'}")
        print()

if __name__ == "__main__":
    main()