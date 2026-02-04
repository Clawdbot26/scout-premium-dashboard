#!/usr/bin/env python3
"""
Daily Brief Generator
Combines all data sources into actionable 8 AM daily reports
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader
import webbrowser
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.settings import get_config

# Import other pipeline components
from news_analyzer import NewsAnalyzer
from technical_screener import TechnicalScreener
from portfolio_monitor import PortfolioMonitor

class DailyBriefGenerator:
    def __init__(self):
        self.config = get_config()
        self.template_dir = "templates"
        self.output_dir = "daily-briefs"
        self.data_dir = "data"
        
        # Initialize components
        self.news_analyzer = NewsAnalyzer()
        self.technical_screener = TechnicalScreener()
        self.portfolio_monitor = PortfolioMonitor()
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir)
        )
        
        # Add custom filters
        self._setup_template_filters()
    
    def _setup_template_filters(self):
        """Setup custom Jinja2 filters for formatting"""
        
        def format_currency(value):
            """Format number as currency"""
            if value is None:
                return "$0.00"
            return f"${value:,.2f}"
        
        def format_percent(value):
            """Format number as percentage"""
            if value is None:
                return "0.0%"
            return f"{value:+.1f}%"
        
        def format_number(value):
            """Format number with commas"""
            if value is None:
                return "0"
            return f"{value:,.0f}"
        
        def format_date(date_string):
            """Format ISO date string"""
            try:
                dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                return dt.strftime("%b %d, %H:%M")
            except:
                return date_string
        
        def sentiment_class(sentiment):
            """Return CSS class for sentiment"""
            sentiment_map = {
                'bullish': 'positive',
                'bearish': 'negative', 
                'neutral': 'neutral'
            }
            return sentiment_map.get(sentiment.lower(), 'neutral')
        
        # Register filters
        self.jinja_env.filters['format_currency'] = format_currency
        self.jinja_env.filters['format_percent'] = format_percent
        self.jinja_env.filters['format_number'] = format_number
        self.jinja_env.filters['format_date'] = format_date
        self.jinja_env.filters['sentiment_class'] = sentiment_class
    
    def collect_all_data(self) -> Dict[str, Any]:
        """Collect data from all pipeline components"""
        print("🔄 Collecting data from all pipeline components...")
        
        data = {
            'timestamp': datetime.now(),
            'date': datetime.now().strftime("%A, %B %d, %Y"),
            'market_open': self._is_market_open(),
        }
        
        try:
            # Portfolio data
            print("📊 Analyzing portfolio...")
            portfolio_summary = self.portfolio_monitor.monitor_portfolio()
            data['portfolio'] = portfolio_summary
            
            # News analysis
            print("📰 Analyzing news...")
            news_articles = self.news_analyzer.fetch_news_articles(days_back=1)
            analyzed_news = self.news_analyzer.analyze_articles(news_articles)
            data['news_articles'] = analyzed_news
            data['news_sentiment'] = self._calculate_news_sentiment(analyzed_news)
            
            # Technical screening
            print("🎯 Running technical screening...")
            screening_results = self.technical_screener.screen_all_stocks()
            data['technical_picks'] = screening_results
            data['top_stock_pick'] = screening_results[0] if screening_results else None
            
            # Sector analysis
            data['sector_analysis'] = self._analyze_sectors(analyzed_news, portfolio_summary)
            
            # Market calendar (placeholder - would integrate with real calendar API)
            data['earnings_today'] = self._get_earnings_calendar()
            data['economic_events'] = self._get_economic_calendar()
            
        except Exception as e:
            print(f"Error collecting data: {e}")
            # Continue with partial data
            pass
        
        return data
    
    def _is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        
        # Simple check - market hours 9:30 AM to 4:00 PM ET on weekdays
        if now.weekday() >= 5:  # Weekend
            return False
        
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def _calculate_news_sentiment(self, articles: List) -> Dict[str, str]:
        """Calculate overall news sentiment by sector"""
        sector_sentiments = {}
        
        # Group articles by sector
        sector_articles = {}
        for article in articles:
            sector = getattr(article, 'sector', 'general')
            if sector not in sector_articles:
                sector_articles[sector] = []
            sector_articles[sector].append(article)
        
        # Calculate sentiment for each sector
        for sector, sector_news in sector_articles.items():
            sentiment_scores = {'bullish': 0, 'bearish': 0, 'neutral': 0}
            
            for article in sector_news:
                sentiment = getattr(article, 'sentiment', 'neutral')
                sentiment_scores[sentiment] += 1
            
            # Determine overall sentiment
            max_sentiment = max(sentiment_scores, key=sentiment_scores.get)
            sector_sentiments[sector] = max_sentiment
        
        # Calculate overall sentiment
        all_sentiments = [getattr(article, 'sentiment', 'neutral') for article in articles]
        overall_sentiment_counts = {'bullish': 0, 'bearish': 0, 'neutral': 0}
        
        for sentiment in all_sentiments:
            overall_sentiment_counts[sentiment] += 1
        
        overall_sentiment = max(overall_sentiment_counts, key=overall_sentiment_counts.get)
        
        return {
            'overall': overall_sentiment,
            'tech': sector_sentiments.get('tech', 'neutral'),
            'finance': sector_sentiments.get('finance', 'neutral'),
            'healthcare': sector_sentiments.get('healthcare', 'neutral'),
            'energy': sector_sentiments.get('energy', 'neutral')
        }
    
    def _analyze_sectors(self, news_articles: List, portfolio_summary) -> Dict[str, Dict]:
        """Analyze each sector with news and portfolio data"""
        sector_analysis = {}
        
        for sector in self.config['sectors'].FOCUS_SECTORS.keys():
            # Filter news for this sector
            sector_news = [article for article in news_articles 
                          if getattr(article, 'sector', '') == sector]
            
            # Calculate sentiment
            if sector_news:
                sentiments = [getattr(article, 'sentiment', 'neutral') for article in sector_news]
                sentiment_counts = {'bullish': 0, 'bearish': 0, 'neutral': 0}
                for sent in sentiments:
                    sentiment_counts[sent] += 1
                sector_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            else:
                sector_sentiment = 'neutral'
            
            # Get top mentioned ticker
            all_tickers = []
            for article in sector_news:
                all_tickers.extend(getattr(article, 'tickers_mentioned', []))
            
            top_ticker = max(set(all_tickers), key=all_tickers.count) if all_tickers else None
            
            sector_analysis[sector] = {
                'sentiment': sector_sentiment,
                'news_count': len(sector_news),
                'top_ticker': top_ticker,
                'high_impact_count': len([a for a in sector_news 
                                        if getattr(a, 'impact_level', '') == 'high'])
            }
        
        return sector_analysis
    
    def _get_earnings_calendar(self) -> List[Dict]:
        """Get today's earnings calendar (placeholder)"""
        # In production, this would connect to an earnings calendar API
        return [
            {'symbol': 'AAPL', 'time': 'After Market Close', 'estimate': '$2.50'},
            {'symbol': 'GOOGL', 'time': 'After Market Close', 'estimate': '$27.50'},
            {'symbol': 'MSFT', 'time': 'After Market Close', 'estimate': '$11.20'},
        ]
    
    def _get_economic_calendar(self) -> List[Dict]:
        """Get today's economic calendar (placeholder)"""
        # In production, this would connect to an economic calendar API
        return [
            {'name': 'CPI Report', 'time': '8:30 AM ET', 'impact': 'High'},
            {'name': 'Fed Speaking', 'time': '2:00 PM ET', 'impact': 'Medium'},
            {'name': 'Jobless Claims', 'time': '8:30 AM ET', 'impact': 'Medium'},
        ]
    
    def generate_brief(self, data: Dict[str, Any], format: str = "html") -> str:
        """Generate the daily brief in specified format"""
        print(f"📝 Generating daily brief in {format.upper()} format...")
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        if format.lower() == "html":
            return self._generate_html_brief(data, timestamp)
        elif format.lower() == "json":
            return self._generate_json_brief(data, timestamp)
        elif format.lower() == "markdown":
            return self._generate_markdown_brief(data, timestamp)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html_brief(self, data: Dict[str, Any], timestamp: str) -> str:
        """Generate HTML brief using template"""
        template = self.jinja_env.get_template('daily_brief_template.html')
        
        # Render template with data
        html_content = template.render(**data)
        
        # Save to file
        filename = f"{self.output_dir}/daily_brief_{timestamp}.html"
        with open(filename, 'w') as f:
            f.write(html_content)
        
        print(f"💾 HTML brief saved to: {filename}")
        return filename
    
    def _generate_json_brief(self, data: Dict[str, Any], timestamp: str) -> str:
        """Generate JSON brief for API consumption"""
        # Convert complex objects to serializable format
        serializable_data = self._make_serializable(data)
        
        filename = f"{self.output_dir}/daily_brief_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(serializable_data, f, indent=2, default=str)
        
        print(f"💾 JSON brief saved to: {filename}")
        return filename
    
    def _generate_markdown_brief(self, data: Dict[str, Any], timestamp: str) -> str:
        """Generate Markdown brief"""
        md_content = f"""# Daily Investment Brief - {data['date']}

## 🎯 Executive Summary

**Portfolio Performance:**
- Total Value: ${data['portfolio'].total_value:,.2f}
- Day Change: ${data['portfolio'].day_change:,.2f} ({data['portfolio'].day_change_pct:+.1f}%)
- Unrealized P&L: ${data['portfolio'].unrealized_pnl:,.2f} ({data['portfolio'].unrealized_pnl_pct:+.1f}%)

**Market Sentiment:** {data['news_sentiment']['overall'].title()}

## 🚨 Critical Alerts

"""
        
        # Add alerts
        critical_alerts = [alert for alert in data['portfolio'].alerts 
                          if alert.severity in ['critical', 'high']]
        
        if critical_alerts:
            for alert in critical_alerts:
                md_content += f"- **{alert.symbol}:** {alert.message}\n"
        else:
            md_content += "- No critical alerts\n"
        
        md_content += f"""
## 📊 Top Positions

| Symbol | Value | Day Change | Total Return | Weight |
|--------|-------|------------|--------------|---------|
"""
        
        for pos in data['portfolio'].positions[:5]:
            md_content += f"| {pos.symbol} | ${pos.current_value:,.0f} | {pos.day_change_pct:+.1f}% | {pos.unrealized_pnl_pct:+.1f}% | {pos.position_size_pct:.1f}% |\n"
        
        md_content += f"""
## 🎯 Top Technical Picks

| Symbol | Score | Recommendation | R:R Ratio | Entry | Target |
|--------|--------|----------------|-----------|-------|---------|
"""
        
        for pick in data['technical_picks'][:5]:
            md_content += f"| {pick.symbol} | {pick.overall_score:.1f} | {pick.recommendation} | {pick.risk_reward_ratio:.1f}:1 | ${pick.entry_price:.2f} | ${pick.target_price:.2f} |\n"
        
        md_content += f"""
## 📰 Key News

"""
        for article in data['news_articles'][:3]:
            md_content += f"- **[{article.sector.upper()}]** {article.title}\n"
            md_content += f"  - Sentiment: {article.sentiment.title()} | Relevance: {article.relevance_score}/100\n"
            md_content += f"  - {article.summary}\n\n"
        
        md_content += f"""
---
*Generated on {timestamp} by Daily Investment Pipeline*

⚠️ This is not financial advice. All investment decisions should be based on your own research and risk tolerance.
"""
        
        filename = f"{self.output_dir}/daily_brief_{timestamp}.md"
        with open(filename, 'w') as f:
            f.write(md_content)
        
        print(f"💾 Markdown brief saved to: {filename}")
        return filename
    
    def _make_serializable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert complex objects to JSON-serializable format"""
        serializable = {}
        
        for key, value in data.items():
            if hasattr(value, '__dict__'):
                # Convert dataclass to dict
                if hasattr(value, '__dataclass_fields__'):
                    serializable[key] = self._dataclass_to_dict(value)
                else:
                    serializable[key] = str(value)
            elif isinstance(value, list):
                serializable[key] = [self._dataclass_to_dict(item) if hasattr(item, '__dataclass_fields__') 
                                   else str(item) for item in value]
            elif isinstance(value, dict):
                serializable[key] = self._make_serializable(value)
            else:
                serializable[key] = value
        
        return serializable
    
    def _dataclass_to_dict(self, obj) -> Dict:
        """Convert dataclass to dictionary"""
        if hasattr(obj, '__dataclass_fields__'):
            result = {}
            for field_name in obj.__dataclass_fields__:
                field_value = getattr(obj, field_name)
                if hasattr(field_value, '__dataclass_fields__'):
                    result[field_name] = self._dataclass_to_dict(field_value)
                elif isinstance(field_value, list):
                    result[field_name] = [self._dataclass_to_dict(item) if hasattr(item, '__dataclass_fields__') 
                                        else item for item in field_value]
                else:
                    result[field_name] = field_value
            return result
        else:
            return str(obj)
    
    def save_data_snapshot(self, data: Dict[str, Any]) -> str:
        """Save raw data snapshot for debugging"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{self.data_dir}/data_snapshot_{timestamp}.json"
        
        serializable_data = self._make_serializable(data)
        
        with open(filename, 'w') as f:
            json.dump(serializable_data, f, indent=2, default=str)
        
        print(f"💾 Data snapshot saved to: {filename}")
        return filename
    
    def open_brief_in_browser(self, html_file: str):
        """Open the generated brief in default browser"""
        file_path = Path(html_file).absolute()
        webbrowser.open(f'file://{file_path}')
        print(f"🌐 Opening brief in browser: {html_file}")

def main():
    """Main execution function"""
    print("🚀 Starting Daily Investment Brief Generation...")
    print(f"📅 Date: {datetime.now().strftime('%A, %B %d, %Y')}")
    print(f"🕐 Time: {datetime.now().strftime('%I:%M %p ET')}")
    print("="*60)
    
    generator = DailyBriefGenerator()
    
    try:
        # Collect all data
        data = generator.collect_all_data()
        
        # Save data snapshot
        generator.save_data_snapshot(data)
        
        # Generate briefs in multiple formats
        html_file = generator.generate_brief(data, format="html")
        json_file = generator.generate_brief(data, format="json") 
        md_file = generator.generate_brief(data, format="markdown")
        
        print("\n✅ Daily Brief Generation Complete!")
        print(f"📄 HTML: {html_file}")
        print(f"📄 JSON: {json_file}")
        print(f"📄 Markdown: {md_file}")
        
        # Open HTML brief in browser
        generator.open_brief_in_browser(html_file)
        
        # Print summary
        portfolio_value = data['portfolio'].total_value if data.get('portfolio') else 0
        alert_count = len(data['portfolio'].alerts) if data.get('portfolio') and data['portfolio'].alerts else 0
        news_count = len(data.get('news_articles', []))
        technical_count = len(data.get('technical_picks', []))
        
        print(f"\n📊 Brief Summary:")
        print(f"   Portfolio Value: ${portfolio_value:,.2f}")
        print(f"   Active Alerts: {alert_count}")
        print(f"   News Articles: {news_count}")
        print(f"   Technical Picks: {technical_count}")
        
        return html_file
        
    except Exception as e:
        print(f"❌ Error generating daily brief: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()