#!/usr/bin/env python3
"""
Demo Daily Brief Generator
Creates a sample daily brief with mock data to show system capabilities
"""

import json
import os
from datetime import datetime
from pathlib import Path

def create_demo_brief():
    """Create a demo daily brief with sample data"""
    
    # Sample data that shows what the system will produce
    sample_data = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%A, %B %d, %Y"),
        "portfolio": {
            "positions": [
                {
                    "symbol": "NVDA",
                    "shares": 50,
                    "current_price": 920.00,
                    "current_value": 46000.00,
                    "unrealized_pnl": 1000.00,
                    "unrealized_pnl_pct": 2.22,
                    "day_change": 250.00,
                    "day_change_pct": 0.54,
                    "position_size_pct": 22.4,
                    "stop_loss_price": 782.00,
                    "target_price": 1150.00
                },
                {
                    "symbol": "TSLA", 
                    "shares": 100,
                    "current_price": 255.00,
                    "current_value": 25500.00,
                    "unrealized_pnl": 500.00,
                    "unrealized_pnl_pct": 2.00,
                    "day_change": 150.00,
                    "day_change_pct": 0.59,
                    "position_size_pct": 12.4,
                    "stop_loss_price": 212.50,
                    "target_price": 320.00
                },
                {
                    "symbol": "MSFT",
                    "shares": 60,
                    "current_price": 435.00,
                    "current_value": 26100.00,
                    "unrealized_pnl": 900.00,
                    "unrealized_pnl_pct": 3.57,
                    "day_change": 180.00,
                    "day_change_pct": 0.69,
                    "position_size_pct": 12.7,
                    "stop_loss_price": 369.75,
                    "target_price": 520.00
                }
            ],
            "alerts": [
                {
                    "symbol": "NVDA",
                    "alert_type": "profit_target",
                    "severity": "medium", 
                    "message": "Price $920 approaching target $1150",
                    "action_recommended": "CONSIDER TAKING PROFITS"
                },
                {
                    "symbol": "PORTFOLIO",
                    "alert_type": "sector_concentration",
                    "severity": "medium",
                    "message": "Tech sector at 47.5% (max: 40.0%)",
                    "action_recommended": "REBALANCE SECTOR ALLOCATION"
                }
            ],
            "sector_allocation": {
                "tech": 47.5,
                "energy": 12.4,
                "cash": 15.0
            },
            "rebalancing_needed": True
        },
        "news_articles": [
            {
                "title": "NVIDIA Reports Strong Q4 Results, AI Demand Continues",
                "source": "Reuters",
                "published_at": "2026-02-01T08:30:00Z",
                "summary": "NVIDIA Corp reported fourth-quarter earnings that beat Wall Street expectations, driven by continued strong demand for AI chips...",
                "sentiment": "bullish",
                "relevance_score": 92,
                "tickers_mentioned": ["NVDA"],
                "sector": "tech",
                "impact_level": "high"
            },
            {
                "title": "Tesla Expands Supercharger Network, Energy Storage Growth",
                "source": "Bloomberg",
                "published_at": "2026-02-01T07:15:00Z", 
                "summary": "Tesla announced plans to expand its Supercharger network by 40% this year while energy storage deployments reached record levels...",
                "sentiment": "bullish",
                "relevance_score": 78,
                "tickers_mentioned": ["TSLA"],
                "sector": "energy",
                "impact_level": "medium"
            },
            {
                "title": "Microsoft Azure Growth Accelerates in Cloud Competition",
                "source": "CNBC",
                "published_at": "2026-02-01T06:45:00Z",
                "summary": "Microsoft's Azure cloud platform showed accelerated growth as enterprise AI adoption drives demand for cloud services...",
                "sentiment": "bullish", 
                "relevance_score": 84,
                "tickers_mentioned": ["MSFT"],
                "sector": "tech",
                "impact_level": "high"
            }
        ],
        "technical_picks": [
            {
                "symbol": "ASML",
                "price": 885.50,
                "overall_score": 87.3,
                "recommendation": "strong_buy",
                "risk_reward_ratio": 3.2,
                "entry_price": 875.00,
                "target_price": 1050.00,
                "sector": "tech"
            },
            {
                "symbol": "V", 
                "price": 295.75,
                "overall_score": 82.1,
                "recommendation": "buy",
                "risk_reward_ratio": 2.8,
                "entry_price": 292.00,
                "target_price": 340.00,
                "sector": "finance"
            },
            {
                "symbol": "UNH",
                "price": 535.25,
                "overall_score": 79.4,
                "recommendation": "buy", 
                "risk_reward_ratio": 2.5,
                "entry_price": 530.00,
                "target_price": 615.00,
                "sector": "healthcare"
            }
        ],
        "news_sentiment": {
            "overall": "bullish",
            "tech": "bullish",
            "finance": "neutral", 
            "healthcare": "neutral",
            "energy": "bullish"
        },
        "sector_analysis": {
            "tech": {
                "sentiment": "bullish",
                "news_count": 8,
                "top_ticker": "NVDA",
                "high_impact_count": 3
            },
            "finance": {
                "sentiment": "neutral", 
                "news_count": 3,
                "top_ticker": "V",
                "high_impact_count": 1
            },
            "healthcare": {
                "sentiment": "neutral",
                "news_count": 2, 
                "top_ticker": "UNH",
                "high_impact_count": 0
            },
            "energy": {
                "sentiment": "bullish",
                "news_count": 4,
                "top_ticker": "TSLA", 
                "high_impact_count": 1
            }
        },
        "earnings_today": [
            {"symbol": "META", "time": "After Market Close", "estimate": "$6.25"},
            {"symbol": "AMZN", "time": "After Market Close", "estimate": "$15.50"}
        ],
        "economic_events": [
            {"name": "Employment Report", "time": "8:30 AM ET", "impact": "High"},
            {"name": "Fed Speaking", "time": "2:00 PM ET", "impact": "Medium"}
        ]
    }
    
    # Create output directories
    os.makedirs("daily-briefs", exist_ok=True)
    
    # Generate JSON version
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    json_filename = f"daily-briefs/demo_brief_{timestamp}.json"
    
    with open(json_filename, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    # Generate HTML version
    html_content = generate_demo_html(sample_data)
    html_filename = f"daily-briefs/demo_brief_{timestamp}.html"
    
    with open(html_filename, 'w') as f:
        f.write(html_content)
    
    # Generate Markdown version
    md_content = generate_demo_markdown(sample_data)
    md_filename = f"daily-briefs/demo_brief_{timestamp}.md"
    
    with open(md_filename, 'w') as f:
        f.write(md_content)
    
    return html_filename, json_filename, md_filename

def generate_demo_html(data):
    """Generate HTML demo brief"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Investment Brief - DEMO</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .header h1 {{ margin: 0; font-size: 2.2em; font-weight: 300; }}
        .demo-badge {{ background: #ff6b6b; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-top: 10px; font-size: 0.9em; }}
        .section {{ padding: 30px; border-bottom: 1px solid #e9ecef; }}
        .section h2 {{ color: #495057; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }}
        .card h3 {{ margin-top: 0; color: #343a40; }}
        .metric {{ display: flex; justify-content: space-between; margin: 8px 0; }}
        .positive {{ color: #28a745; font-weight: 600; }}
        .negative {{ color: #dc3545; font-weight: 600; }}
        .alert {{ padding: 15px; margin: 10px 0; border-radius: 5px; background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        .table th, .table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e9ecef; }}
        .table th {{ background: #f8f9fa; font-weight: 600; }}
        .news-item {{ margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #17a2b8; }}
        .rec-badge {{ padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: 600; color: white; background: #28a745; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Daily Investment Brief</h1>
            <div class="demo-badge">🎯 DEMO VERSION</div>
            <div style="margin-top: 10px;">{data['date']} • Sample Data</div>
        </div>

        <div class="section">
            <h2>🎯 Executive Summary</h2>
            <div class="grid">
                <div class="card">
                    <h3>Portfolio Performance</h3>
                    <div class="metric">
                        <span>Total Value:</span>
                        <span>${data['portfolio']['total_value']:,.2f}</span>
                    </div>
                    <div class="metric">
                        <span>Day Change:</span>
                        <span class="positive">${data['portfolio']['day_change']:,.2f} (+{data['portfolio']['day_change_pct']:.1f}%)</span>
                    </div>
                    <div class="metric">
                        <span>Unrealized P&L:</span>
                        <span class="positive">${data['portfolio']['unrealized_pnl']:,.2f} (+{data['portfolio']['unrealized_pnl_pct']:.1f}%)</span>
                    </div>
                </div>

                <div class="card">
                    <h3>Market Sentiment</h3>
                    <div class="metric">
                        <span>Overall:</span>
                        <span class="positive">{data['news_sentiment']['overall'].title()}</span>
                    </div>
                    <div class="metric">
                        <span>Tech Sector:</span>
                        <span class="positive">{data['news_sentiment']['tech'].title()}</span>
                    </div>
                    <div class="metric">
                        <span>Active Alerts:</span>
                        <span>{len(data['portfolio']['alerts'])}</span>
                    </div>
                </div>

                <div class="card">
                    <h3>Today's Focus</h3>
                    <div class="metric">
                        <span>Top Pick:</span>
                        <span>{data['technical_picks'][0]['symbol']}</span>
                    </div>
                    <div class="metric">
                        <span>Earnings Today:</span>
                        <span>{len(data['earnings_today'])} companies</span>
                    </div>
                    <div class="metric">
                        <span>News Articles:</span>
                        <span>{len(data['news_articles'])}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🚨 Active Alerts</h2>
            {' '.join([f'<div class="alert"><strong>{alert["symbol"]}:</strong> {alert["message"]}<br><small>Action: {alert["action_recommended"]}</small></div>' for alert in data['portfolio']['alerts']])}
        </div>

        <div class="section">
            <h2>📊 Portfolio Positions</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Shares</th>
                        <th>Current Price</th>
                        <th>Value</th>
                        <th>Day Change</th>
                        <th>Total Return</th>
                        <th>Weight</th>
                    </tr>
                </thead>
                <tbody>
                    {' '.join([f'''<tr>
                        <td><strong>{pos['symbol']}</strong></td>
                        <td>{pos['shares']}</td>
                        <td>${pos['current_price']:.2f}</td>
                        <td>${pos['current_value']:,.0f}</td>
                        <td class="positive">${pos['day_change']:.0f} (+{pos['day_change_pct']:.1f}%)</td>
                        <td class="positive">${pos['unrealized_pnl']:.0f} (+{pos['unrealized_pnl_pct']:.1f}%)</td>
                        <td>{pos['position_size_pct']:.1f}%</td>
                    </tr>''' for pos in data['portfolio']['positions']])}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>📈 Top Technical Opportunities</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Price</th>
                        <th>Score</th>
                        <th>Recommendation</th>
                        <th>R:R Ratio</th>
                        <th>Entry</th>
                        <th>Target</th>
                    </tr>
                </thead>
                <tbody>
                    {' '.join([f'''<tr>
                        <td><strong>{pick['symbol']}</strong></td>
                        <td>${pick['price']:.2f}</td>
                        <td>{pick['overall_score']:.1f}</td>
                        <td><span class="rec-badge">{pick['recommendation'].upper()}</span></td>
                        <td>{pick['risk_reward_ratio']:.1f}:1</td>
                        <td>${pick['entry_price']:.2f}</td>
                        <td>${pick['target_price']:.2f}</td>
                    </tr>''' for pick in data['technical_picks']])}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>📰 Key News & Analysis</h2>
            {' '.join([f'''<div class="news-item">
                <div style="font-weight: 600; color: #343a40;">{article['title']}</div>
                <div style="font-size: 0.9em; color: #6c757d; margin: 8px 0;">
                    {article['source']} • {article['sentiment'].title()} Sentiment • Relevance: {article['relevance_score']}/100
                    • Tickers: {', '.join(article['tickers_mentioned'])}
                </div>
                <div style="color: #495057;">{article['summary']}</div>
            </div>''' for article in data['news_articles']])}
        </div>

        <div class="section">
            <h2>✅ Action Items</h2>
            <div class="grid">
                <div class="card">
                    <h3>Immediate Actions</h3>
                    <ul>
                        <li><strong>NVDA:</strong> Consider taking profits at current levels</li>
                        <li><strong>Portfolio:</strong> Rebalance tech sector allocation</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>Research Opportunities</h3>
                    <ul>
                        <li>Research ASML entry opportunity (Score: 87.3)</li>
                        <li>Monitor V payment processing trends</li>
                        <li>Review UNH healthcare consolidation</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>Risk Management</h3>
                    <ul>
                        <li>Portfolio rebalancing recommended</li>
                        <li>Review stop-loss levels on all positions</li>
                        <li>Monitor sector concentration limits</li>
                    </ul>
                </div>
            </div>
        </div>

        <div style="background: #343a40; color: #adb5bd; padding: 20px; text-align: center;">
            Generated on {data['timestamp']} • Daily Investment Pipeline DEMO<br>
            <small>⚠️ This is sample data for demonstration purposes only. Not financial advice.</small>
        </div>
    </div>
</body>
</html>"""

def generate_demo_markdown(data):
    """Generate Markdown demo brief"""
    return f"""# Daily Investment Brief - DEMO

**{data['date']}** | Sample Data Demonstration

## 🎯 Executive Summary

**Portfolio Performance:**
- Total Value: ${data['portfolio']['total_value']:,.2f}
- Day Change: ${data['portfolio']['day_change']:,.2f} (+{data['portfolio']['day_change_pct']:.1f}%)
- Unrealized P&L: ${data['portfolio']['unrealized_pnl']:,.2f} (+{data['portfolio']['unrealized_pnl_pct']:.1f}%)

**Market Sentiment:** {data['news_sentiment']['overall'].title()}

## 🚨 Active Alerts

- **NVDA:** {data['portfolio']['alerts'][0]['message']}
- **PORTFOLIO:** {data['portfolio']['alerts'][1]['message']}

## 📊 Top Positions

| Symbol | Value | Day Change | Total Return | Weight |
|--------|-------|------------|--------------|---------|
| NVDA | ${data['portfolio']['positions'][0]['current_value']:,.0f} | +{data['portfolio']['positions'][0]['day_change_pct']:.1f}% | +{data['portfolio']['positions'][0]['unrealized_pnl_pct']:.1f}% | {data['portfolio']['positions'][0]['position_size_pct']:.1f}% |
| TSLA | ${data['portfolio']['positions'][1]['current_value']:,.0f} | +{data['portfolio']['positions'][1]['day_change_pct']:.1f}% | +{data['portfolio']['positions'][1]['unrealized_pnl_pct']:.1f}% | {data['portfolio']['positions'][1]['position_size_pct']:.1f}% |
| MSFT | ${data['portfolio']['positions'][2]['current_value']:,.0f} | +{data['portfolio']['positions'][2]['day_change_pct']:.1f}% | +{data['portfolio']['positions'][2]['unrealized_pnl_pct']:.1f}% | {data['portfolio']['positions'][2]['position_size_pct']:.1f}% |

## 🎯 Top Technical Picks

| Symbol | Score | Recommendation | R:R Ratio | Entry | Target |
|--------|--------|----------------|-----------|-------|---------|
| ASML | {data['technical_picks'][0]['overall_score']:.1f} | {data['technical_picks'][0]['recommendation'].upper()} | {data['technical_picks'][0]['risk_reward_ratio']:.1f}:1 | ${data['technical_picks'][0]['entry_price']:.2f} | ${data['technical_picks'][0]['target_price']:.2f} |
| V | {data['technical_picks'][1]['overall_score']:.1f} | {data['technical_picks'][1]['recommendation'].upper()} | {data['technical_picks'][1]['risk_reward_ratio']:.1f}:1 | ${data['technical_picks'][1]['entry_price']:.2f} | ${data['technical_picks'][1]['target_price']:.2f} |
| UNH | {data['technical_picks'][2]['overall_score']:.1f} | {data['technical_picks'][2]['recommendation'].upper()} | {data['technical_picks'][2]['risk_reward_ratio']:.1f}:1 | ${data['technical_picks'][2]['entry_price']:.2f} | ${data['technical_picks'][2]['target_price']:.2f} |

## 📰 Key News

- **[TECH]** {data['news_articles'][0]['title']}
  - Sentiment: {data['news_articles'][0]['sentiment'].title()} | Relevance: {data['news_articles'][0]['relevance_score']}/100
  - {data['news_articles'][0]['summary']}

- **[ENERGY]** {data['news_articles'][1]['title']}
  - Sentiment: {data['news_articles'][1]['sentiment'].title()} | Relevance: {data['news_articles'][1]['relevance_score']}/100
  - {data['news_articles'][1]['summary']}

- **[TECH]** {data['news_articles'][2]['title']}
  - Sentiment: {data['news_articles'][2]['sentiment'].title()} | Relevance: {data['news_articles'][2]['relevance_score']}/100
  - {data['news_articles'][2]['summary']}

## ✅ Action Items

**Immediate Actions:**
- NVDA: Consider taking profits at current levels
- Portfolio: Rebalance tech sector allocation

**Research Opportunities:**
- Research ASML entry opportunity (Score: 87.3)
- Monitor V payment processing trends
- Review UNH healthcare consolidation

**Risk Management:**
- Portfolio rebalancing recommended
- Review stop-loss levels on all positions
- Monitor sector concentration limits

---

*Generated on {data['timestamp']} by Daily Investment Pipeline DEMO*

⚠️ **This is sample data for demonstration purposes only. Not financial advice.**
"""

def main():
    """Generate demo brief"""
    print("🎯 Generating Demo Daily Investment Brief...")
    
    try:
        html_file, json_file, md_file = create_demo_brief()
        
        print(f"""
✅ Demo Brief Generated Successfully!

📄 Files created:
   • HTML: {html_file}
   • JSON: {json_file}  
   • Markdown: {md_file}

🌐 Open the HTML file in your browser to see the full formatted report.

📊 This demo shows what your daily briefs will look like once the system is set up with real data:
   • Portfolio performance tracking
   • Technical analysis and stock picks
   • News analysis with sentiment
   • Actionable alerts and recommendations

🚀 To set up the real system:
   1. Run: ./setup.sh
   2. Install dependencies: pip install -r requirements.txt  
   3. Configure your portfolio: edit config/portfolio.json
   4. Generate real brief: python scripts/generate_daily_brief.py
        """)
        
        return html_file
        
    except Exception as e:
        print(f"❌ Error generating demo brief: {e}")
        return None

if __name__ == "__main__":
    main()