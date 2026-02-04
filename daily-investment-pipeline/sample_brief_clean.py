#!/usr/bin/env python3
"""
Generate a clean sample daily brief without personal financial details
Shows system capabilities and format without actual portfolio values
"""

from datetime import datetime
import json

def generate_clean_brief():
    """Generate sample brief focusing on system capabilities, not personal finance"""
    
    brief_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "executive_summary": {
            "market_sentiment": "Mixed with tech leading",
            "key_focus": "3 technical opportunities identified",
            "alerts_count": 2,
            "news_items": 5
        },
        "critical_alerts": [
            {
                "type": "Technical Opportunity", 
                "message": "ASML showing strong breakout setup - Score 87.3/100",
                "priority": "High"
            },
            {
                "type": "Sector Rotation",
                "message": "Healthcare showing relative strength vs tech",
                "priority": "Medium"
            }
        ],
        "technical_opportunities": [
            {
                "ticker": "ASML",
                "score": 87.3,
                "recommendation": "Strong Buy",
                "entry_price": "$856.00",
                "target_price": "$920.00", 
                "stop_loss": "$825.00",
                "risk_reward": "2.3:1",
                "setup": "Bullish pennant breakout with volume confirmation"
            },
            {
                "ticker": "V",
                "score": 82.1,
                "recommendation": "Buy",
                "entry_price": "$315.00",
                "target_price": "$335.00",
                "stop_loss": "$305.00", 
                "risk_reward": "2.0:1",
                "setup": "Support bounce with RSI oversold recovery"
            },
            {
                "ticker": "UNH",
                "score": 79.8,
                "recommendation": "Buy",
                "entry_price": "$595.00",
                "target_price": "$620.00",
                "stop_loss": "$580.00",
                "risk_reward": "1.7:1",
                "setup": "Healthcare sector momentum with earnings tailwind"
            }
        ],
        "news_analysis": [
            {
                "headline": "ASML Reports Strong Q4 Bookings, AI Chip Demand Surge",
                "sentiment": "Bullish",
                "relevance_score": 92,
                "impact": "High",
                "tickers_mentioned": ["ASML", "NVDA", "TSM"],
                "summary": "Equipment demand for advanced AI chips driving record bookings"
            },
            {
                "headline": "Healthcare Sector Rotation Accelerates as Tech Cools",
                "sentiment": "Neutral",
                "relevance_score": 78,
                "impact": "Medium",
                "tickers_mentioned": ["UNH", "JNJ", "PFE"],
                "summary": "Defensive positioning driving healthcare outperformance"
            }
        ],
        "market_calendar": [
            {
                "time": "08:30 AM",
                "event": "Initial Jobless Claims",
                "importance": "Medium",
                "forecast": "220K"
            },
            {
                "time": "After Close",
                "event": "V Earnings Release",
                "importance": "High",
                "forecast": "EPS $2.68"
            }
        ],
        "action_items": [
            {
                "category": "Research",
                "task": "Investigate ASML breakout setup - strong technical score",
                "priority": "High",
                "timeframe": "Today"
            },
            {
                "category": "Monitoring", 
                "task": "Watch V earnings reaction for entry opportunity",
                "priority": "Medium",
                "timeframe": "After close"
            },
            {
                "category": "Sector Analysis",
                "task": "Review healthcare rotation strength - UNH setup",
                "priority": "Medium", 
                "timeframe": "This week"
            }
        ]
    }
    
    return brief_data

def create_html_template(data):
    """Generate clean HTML template focusing on system capabilities"""
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Daily Investment Brief - {data['timestamp'][:10]}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #1a365d; color: white; padding: 20px; border-radius: 8px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #e2e8f0; border-radius: 8px; }}
        .alert-high {{ background: #fed7d7; border-left: 4px solid #e53e3e; }}
        .alert-medium {{ background: #feebc8; border-left: 4px solid #dd6b20; }}
        .opportunity {{ background: #f0fff4; border-left: 4px solid #38a169; }}
        .news-bullish {{ color: #38a169; font-weight: bold; }}
        .news-bearish {{ color: #e53e3e; font-weight: bold; }}
        .news-neutral {{ color: #718096; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f7fafc; font-weight: bold; }}
        .score {{ font-weight: bold; color: #38a169; }}
        .action-high {{ background: #fed7d7; }}
        .action-medium {{ background: #feebc8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Daily Investment Brief</h1>
        <p>Generated: {data['timestamp']} | Market Analysis & Opportunities</p>
    </div>
    
    <div class="section">
        <h2>📊 Executive Summary</h2>
        <ul>
            <li><strong>Market Sentiment:</strong> {data['executive_summary']['market_sentiment']}</li>
            <li><strong>Key Focus:</strong> {data['executive_summary']['key_focus']}</li>
            <li><strong>Active Alerts:</strong> {data['executive_summary']['alerts_count']}</li>
            <li><strong>News Items:</strong> {data['executive_summary']['news_items']}</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>🚨 Critical Alerts</h2>
        {''.join([f'<div class="alert-{alert["priority"].lower()}"><strong>{alert["type"]}:</strong> {alert["message"]}</div>' for alert in data['critical_alerts']])}
    </div>
    
    <div class="section opportunity">
        <h2>📈 Top Technical Opportunities</h2>
        <table>
            <tr>
                <th>Ticker</th>
                <th>Score</th>
                <th>Recommendation</th>
                <th>Entry</th>
                <th>Target</th>
                <th>Stop Loss</th>
                <th>R:R</th>
                <th>Setup</th>
            </tr>"""
    
    for opp in data['technical_opportunities']:
        html += f"""
            <tr>
                <td><strong>{opp['ticker']}</strong></td>
                <td class="score">{opp['score']}</td>
                <td>{opp['recommendation']}</td>
                <td>{opp['entry_price']}</td>
                <td>{opp['target_price']}</td>
                <td>{opp['stop_loss']}</td>
                <td>{opp['risk_reward']}</td>
                <td>{opp['setup']}</td>
            </tr>"""
    
    html += """
        </table>
    </div>
    
    <div class="section">
        <h2>📰 News Analysis</h2>"""
    
    for news in data['news_analysis']:
        sentiment_class = f"news-{news['sentiment'].lower()}"
        html += f"""
        <div style="margin: 15px 0; padding: 10px; border-left: 3px solid #e2e8f0;">
            <h4>{news['headline']}</h4>
            <p><span class="{sentiment_class}">Sentiment: {news['sentiment']}</span> | 
               Relevance: {news['relevance_score']}/100 | 
               Impact: {news['impact']}</p>
            <p><strong>Tickers:</strong> {', '.join(news['tickers_mentioned'])}</p>
            <p>{news['summary']}</p>
        </div>"""
    
    html += """
    </div>
    
    <div class="section">
        <h2>📅 Market Calendar</h2>
        <table>
            <tr><th>Time</th><th>Event</th><th>Importance</th><th>Forecast</th></tr>"""
    
    for event in data['market_calendar']:
        html += f"""
            <tr>
                <td>{event['time']}</td>
                <td>{event['event']}</td>
                <td>{event['importance']}</td>
                <td>{event['forecast']}</td>
            </tr>"""
    
    html += """
        </table>
    </div>
    
    <div class="section">
        <h2>✅ Action Items</h2>
        <table>
            <tr><th>Category</th><th>Task</th><th>Priority</th><th>Timeframe</th></tr>"""
    
    for action in data['action_items']:
        priority_class = f"action-{action['priority'].lower()}"
        html += f"""
            <tr class="{priority_class}">
                <td>{action['category']}</td>
                <td>{action['task']}</td>
                <td>{action['priority']}</td>
                <td>{action['timeframe']}</td>
            </tr>"""
    
    html += """
        </table>
    </div>
    
    <div class="section">
        <p><em>This brief combines news analysis, technical screening, and market intelligence 
        into actionable investment insights. Generated automatically by the Daily Investment Research Pipeline.</em></p>
    </div>
    
</body>
</html>
    """
    
    return html

if __name__ == "__main__":
    # Generate sample data
    brief_data = generate_clean_brief()
    
    # Create HTML version
    html_content = create_html_template(brief_data)
    
    # Save files
    with open('sample_clean_brief.html', 'w') as f:
        f.write(html_content)
    
    with open('sample_clean_brief.json', 'w') as f:
        json.dump(brief_data, f, indent=2)
    
    print("✅ Clean sample brief generated:")
    print("  📄 sample_clean_brief.html - Visual dashboard")
    print("  📊 sample_clean_brief.json - Raw data")
    print("\n🔍 Open the HTML file to see your daily brief format!")