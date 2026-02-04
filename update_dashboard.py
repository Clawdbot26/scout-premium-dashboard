#!/usr/bin/env python3
"""
Scout Premium Dashboard Auto-Updater (v2)
Dynamically scores stocks and updates top 7 + watchlist
"""

import yfinance as yf
from datetime import datetime, timedelta
import json
import re
import subprocess
import math
from pathlib import Path

# All stocks to evaluate
STOCKS = {
    'PLTR': 'PALANTIR TECHNOLOGIES',
    'CRM': 'SALESFORCE',
    'AMAT': 'APPLIED MATERIALS',
    'ASML': 'ASML HOLDING',
    'NVDA': 'NVIDIA',
    'AVGO': 'BROADCOM',
    'MRVL': 'MARVELL TECHNOLOGY',
    'AMD': 'AMD',
    'COHR': 'COHERENT',
}

# Historical peer averages for context
PEER_BENCHMARKS = {
    'PLTR': {'avg_pe': 100, 'avg_growth': 20, 'sector': 'Defense/Software'},
    'CRM': {'avg_pe': 30, 'avg_growth': 12, 'sector': 'Enterprise Software'},
    'AMAT': {'avg_pe': 35, 'avg_growth': 18, 'sector': 'Semiconductors'},
    'ASML': {'avg_pe': 45, 'avg_growth': 8, 'sector': 'Semiconductors'},
    'NVDA': {'avg_pe': 35, 'avg_growth': 25, 'sector': 'Semiconductors'},
    'AVGO': {'avg_pe': 35, 'avg_growth': 12, 'sector': 'Semiconductors'},
    'MRVL': {'avg_pe': 35, 'avg_growth': 16, 'sector': 'Semiconductors'},
    'AMD': {'avg_pe': 35, 'avg_growth': 20, 'sector': 'Semiconductors'},
    'COHR': {'avg_pe': 45, 'avg_growth': 15, 'sector': 'Semiconductors'},
}

def fetch_comprehensive_data(ticker):
    """Fetch all data needed for scoring"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Historical data for technical analysis
        hist = stock.history(period="6mo")
        if hist.empty:
            return None
        
        # Current metrics
        current_price = hist['Close'].iloc[-1]
        price_52w_high = hist['Close'].max()
        price_52w_low = hist['Close'].min()
        
        # Change calculations
        price_1m_ago = hist['Close'].iloc[-22] if len(hist) > 22 else hist['Close'].iloc[0]
        price_1w_ago = hist['Close'].iloc[-5] if len(hist) > 5 else hist['Close'].iloc[0]
        change_1d = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0
        change_1w = ((current_price - price_1w_ago) / price_1w_ago * 100) if price_1w_ago else 0
        change_1m = ((current_price - price_1m_ago) / price_1m_ago * 100) if price_1m_ago else 0
        
        # Valuation metrics
        pe = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        ps = info.get('priceToSalesTrailing12Months', None)
        
        # Growth metrics
        revenue_growth = info.get('revenueGrowth', None)
        earnings_growth = info.get('earningsGrowth', None)
        
        # Technical
        beta = info.get('beta', 1.0)
        rsi = calculate_rsi(hist['Close'], 14)
        
        # Volume trends
        avg_volume_30d = hist['Volume'].tail(30).mean()
        current_volume = hist['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume_30d if avg_volume_30d > 0 else 1.0
        
        # Momentum (3-month trend)
        momentum = change_1m / 100 if change_1m else 0
        
        return {
            'ticker': ticker,
            'name': STOCKS[ticker],
            'price': round(current_price, 2),
            'change_1d': round(change_1d, 2),
            'change_1w': round(change_1w, 2),
            'change_1m': round(change_1m, 2),
            'volume': int(current_volume),
            'avg_volume_30d': int(avg_volume_30d),
            'volume_ratio': round(volume_ratio, 2),
            'pe': pe,
            'forward_pe': forward_pe,
            'ps': ps,
            'revenue_growth': revenue_growth,
            'earnings_growth': earnings_growth,
            'beta': round(beta, 2) if beta else 1.0,
            'rsi': round(rsi, 1),
            'momentum': round(momentum, 2),
            'price_52w_high': round(price_52w_high, 2),
            'price_52w_low': round(price_52w_low, 2),
        }
    except Exception as e:
        print(f"  ⚠️  {ticker}: {str(e)[:50]}")
        return None

def calculate_rsi(prices, period=14):
    """Calculate RSI (Relative Strength Index)"""
    if len(prices) < period:
        return 50
    
    deltas = prices.diff()
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    
    if down == 0:
        return 100 if up > 0 else 50
    
    rs = up / down
    rsi = 100 - (100 / (1 + rs))
    
    for i in range(period+1, len(deltas)):
        delta = deltas.iloc[i]
        if delta > 0:
            up = (up * (period - 1) + delta) / period
            down = down * (period - 1) / period
        else:
            up = up * (period - 1) / period
            down = (-delta + down * (period - 1)) / period
        
        rs = up / down if down != 0 else rs
        rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_value_score(data):
    """
    Calculate Value Score (1-10 scale)
    
    Factors:
    - Valuation (P/E vs peers, growth-adjusted) — 30%
    - Growth (revenue + earnings growth rate) — 25%
    - Technical (RSI strength + momentum) — 20%
    - Volume (accumulation signals) — 15%
    - Risk-adjusted (beta consideration) — 10%
    """
    
    ticker = data['ticker']
    benchmark = PEER_BENCHMARKS.get(ticker, {'avg_pe': 40, 'avg_growth': 15})
    
    scores = {}
    
    # 1. Valuation Score (30%)
    # Lower P/E relative to growth = higher score
    if data['pe'] and data['pe'] > 0:
        peg_ratio = data['pe'] / (data['revenue_growth'] * 100) if data['revenue_growth'] and data['revenue_growth'] > 0 else 10
        # PEG < 1.5 = great, < 2.0 = good, > 3.0 = expensive
        if peg_ratio < 1.0:
            val_score = 10
        elif peg_ratio < 1.5:
            val_score = 8.5
        elif peg_ratio < 2.0:
            val_score = 7.5
        elif peg_ratio < 3.0:
            val_score = 6.0
        else:
            val_score = 4.0
    else:
        val_score = 5.0  # Unknown
    
    scores['valuation'] = val_score
    
    # 2. Growth Score (25%)
    # Revenue growth > 20% = excellent, > 15% = good, > 10% = solid
    if data['revenue_growth']:
        growth_pct = data['revenue_growth'] * 100
        if growth_pct > 30:
            growth_score = 10
        elif growth_pct > 20:
            growth_score = 9
        elif growth_pct > 15:
            growth_score = 8
        elif growth_pct > 10:
            growth_score = 7
        elif growth_pct > 5:
            growth_score = 6
        else:
            growth_score = 4
    else:
        growth_score = 5
    
    scores['growth'] = growth_score
    
    # 3. Technical Score (20%)
    # RSI 40-60 = healthy, momentum + positive trend = boost
    rsi = data['rsi']
    if rsi > 30 and rsi < 70:
        technical_base = 7
    elif rsi > 20 and rsi < 80:
        technical_base = 6
    else:
        technical_base = 4
    
    # Boost for positive momentum
    if data['change_1m'] > 10:
        technical_score = min(10, technical_base + 2)
    elif data['change_1m'] > 0:
        technical_score = technical_base + 1
    elif data['change_1m'] > -5:
        technical_score = technical_base
    else:
        technical_score = max(3, technical_base - 1)
    
    scores['technical'] = technical_score
    
    # 4. Volume Score (15%)
    # High volume on momentum = accumulation signal
    if data['volume_ratio'] > 1.5 and data['change_1w'] > 0:
        volume_score = 9
    elif data['volume_ratio'] > 1.2 and data['change_1w'] > 0:
        volume_score = 8
    elif data['volume_ratio'] > 1.0 and data['change_1m'] > 0:
        volume_score = 7
    elif data['volume_ratio'] > 0.8:
        volume_score = 6
    else:
        volume_score = 5
    
    scores['volume'] = volume_score
    
    # 5. Risk-Adjusted Score (10%)
    # Lower beta = safer, but we want growth too
    # Beta 1.0-1.5 = ideal, > 2.0 = risky
    beta = data['beta']
    if beta < 1.2:
        risk_score = 9
    elif beta < 1.5:
        risk_score = 8
    elif beta < 1.8:
        risk_score = 7
    elif beta < 2.2:
        risk_score = 6
    else:
        risk_score = 4
    
    scores['risk'] = risk_score
    
    # Calculate weighted final score (1-10)
    weights = {
        'valuation': 0.30,
        'growth': 0.25,
        'technical': 0.20,
        'volume': 0.15,
        'risk': 0.10,
    }
    
    final_score = sum(scores[k] * weights[k] for k in scores.keys())
    final_score = round(final_score, 1)
    
    return final_score, scores

def main():
    print("🚀 Scout Dashboard Auto-Updater (Dynamic Scoring)")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S EDT')}")
    print()
    
    # Fetch all stock data
    print("📡 Fetching market data for 9 stocks...")
    all_data = {}
    for ticker in STOCKS.keys():
        data = fetch_comprehensive_data(ticker)
        if data:
            all_data[ticker] = data
            print(f"  ✅ {ticker}: ${data['price']}")
        else:
            print(f"  ⚠️  {ticker}: Failed")
    
    print()
    
    if len(all_data) < 5:
        print("❌ Not enough data fetched. Aborting.")
        return
    
    # Calculate scores for all stocks
    print("🎯 Calculating Value Scores...")
    scored_stocks = {}
    for ticker, data in all_data.items():
        score, details = calculate_value_score(data)
        data['value_score'] = score
        data['score_details'] = details
        scored_stocks[ticker] = data
        print(f"  {ticker:5} → {score}/10 (Val:{details['valuation']:.1f} | Growth:{details['growth']:.1f} | Tech:{details['technical']:.1f})")
    
    print()
    
    # Filter to top 7 (7.0+) and watchlist (6.5-7.0)
    sorted_stocks = sorted(scored_stocks.items(), key=lambda x: x[1]['value_score'], reverse=True)
    
    top_7 = {k: v for k, v in sorted_stocks if v['value_score'] >= 7.0}
    watchlist = {k: v for k, v in sorted_stocks if 6.5 <= v['value_score'] < 7.0}
    
    print(f"📊 Results:")
    print(f"  🔥 Top 7 (≥7.0): {len(top_7)} stocks")
    for ticker, data in list(sorted_stocks[:7]):
        status = "✅ TOP 7" if data['value_score'] >= 7.0 else "👀 WATCHLIST"
        print(f"     {ticker:5} {data['value_score']}/10 {status}")
    
    if watchlist:
        print(f"  👀 Watchlist (6.5-7.0): {len(watchlist)} stocks")
        for ticker, data in watchlist.items():
            print(f"     {ticker:5} {data['value_score']}/10")
    
    print()
    
    # Save scoring data to JSON for reference
    scoring_data = {
        'timestamp': datetime.now().isoformat(),
        'top_7': {k: {'score': v['value_score'], 'price': v['price'], 'change_1d': v['change_1d']} for k, v in list(sorted_stocks[:7])},
        'watchlist': {k: {'score': v['value_score'], 'price': v['price']} for k, v in watchlist.items()},
        'all_scores': {k: v['value_score'] for k, v in scored_stocks.items()}
    }
    
    with open('/Users/clawdbot/.openclaw/workspace/.dashboard-scores.json', 'w') as f:
        json.dump(scoring_data, f, indent=2)
    
    # Update HTML with new top 7
    print("📝 Updating dashboard...")
    update_dashboard_html(top_7, watchlist, scored_stocks)
    
    print()
    
    # Commit and push
    print("🔄 Pushing to GitHub...")
    git_commit_and_push(top_7, watchlist)
    
    print()
    print("✨ Dashboard update complete!")
    print(f"   📊 Live: https://clawdbot26.github.io/scout-premium-dashboard/")

def update_dashboard_html(top_7, watchlist, all_stocks):
    """Update HTML with dynamically sorted top 7"""
    html_file = Path('/Users/clawdbot/.openclaw/workspace/dashboard-premium.html')
    
    with open(html_file, 'r') as f:
        html = f.read()
    
    # Update timestamp
    now = datetime.now().strftime("%B %d, %Y | %I:%M %p EST")
    html = re.sub(
        r'<div>.*?\|\s*\d+:\d+\s[AP]M EST.*?</div>',
        f'<div>{now} | Real-Time Data</div>',
        html,
        flags=re.DOTALL,
        count=1
    )
    
    html = re.sub(
        r'Last Updated:.*?<br/>',
        f'Last Updated: {now}<br/>',
        html
    )
    
    # Update top 7 stock prices in detail cards
    for ticker, data in list(top_7.items())[:7]:
        price = data['price']
        change = data['change_1d']
        score = data['value_score']
        color = '#00ff88' if change >= 0 else '#ff4444'
        sign = '+' if change >= 0 else ''
        
        # Update in stock cards
        pattern = rf'(<div class="stock-price">)[^<]*{ticker}[^<]*?</div>'
        replacement = f'<div class="stock-price">${price} <span style="color: {color}; font-size: 12px;">{sign}{change}%</span></div>'
        html = re.sub(pattern, replacement, html, count=1)
    
    # Save
    with open(html_file, 'w') as f:
        f.write(html)
    
    print("  ✅ HTML updated")

def git_commit_and_push(top_7, watchlist):
    """Commit and push changes"""
    try:
        repo_path = Path('/Users/clawdbot/.openclaw/workspace')
        
        # Check for changes
        result = subprocess.run(
            ['git', 'diff', '--quiet', 'dashboard-premium.html'],
            cwd=repo_path,
            capture_output=True
        )
        
        if result.returncode == 0:
            print("  ⏭️  No price changes to commit")
            return
        
        # Commit
        top_tickers = ', '.join(list(top_7.keys())[:3])
        subprocess.run(['git', 'add', 'dashboard-premium.html'], cwd=repo_path, check=True)
        subprocess.run(
            ['git', 'commit', '-m', f'chore: Auto-update scores and prices\n\nTop 7: {top_tickers}...'],
            cwd=repo_path,
            check=True
        )
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=repo_path, check=True)
        
        print("  ✅ Pushed to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Git error: {e}")

if __name__ == '__main__':
    main()
