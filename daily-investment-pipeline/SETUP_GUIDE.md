# 🚀 Daily Investment Pipeline - Setup Guide

Complete setup instructions for Roni's automated investment research system.

## 📋 Prerequisites

- Python 3.8+ installed
- Terminal/Command line access
- Internet connection for data fetching
- (Optional) API keys for enhanced data sources

## 🎯 Quick Setup (5 minutes)

```bash
# 1. Navigate to the pipeline directory
cd daily-investment-pipeline

# 2. Run the automated setup
./setup.sh

# 3. Configure your portfolio (see step 4 below)
nano config/portfolio.json

# 4. Test the system
source venv/bin/activate
python scripts/generate_daily_brief.py

# 5. Check your daily-briefs/ directory for results!
```

## 📖 Detailed Setup Instructions

### Step 1: System Requirements

**Required:**
- Python 3.8+ (`python3 --version`)
- pip package manager
- At least 1GB free disk space

**Check your Python version:**
```bash
python3 --version
# Should show Python 3.8.0 or higher
```

### Step 2: Installation

**Option A: Automated Setup (Recommended)**
```bash
cd daily-investment-pipeline
./setup.sh
```

**Option B: Manual Setup**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p daily-briefs portfolio-tracking news-analysis technical-screening data logs

# Make scripts executable
chmod +x scripts/*.py
```

### Step 3: Configure Your Portfolio

Edit `config/portfolio.json` with your actual positions:

```json
{
  "portfolio_metadata": {
    "total_value": 200000,
    "last_updated": "2026-02-01"
  },
  "positions": [
    {
      "symbol": "NVDA",
      "shares": 50,
      "avg_cost": 900.00,
      "entry_date": "2025-12-15",
      "stop_loss": 765.00,
      "target_price": 1200.00,
      "notes": "AI semiconductor leader"
    }
  ],
  "cash_position": {
    "amount": 50000,
    "percentage": 0.25
  }
}
```

**Important fields to update:**
- `total_value`: Your actual portfolio value
- `positions`: Your actual stock positions
- `cash_position`: Your current cash holdings

### Step 4: API Keys (Optional but Recommended)

Copy the credentials template:
```bash
cp config/credentials.env.template config/credentials.env
```

Edit `config/credentials.env` and add your API keys:

```bash
# Market Data (choose one)
ALPHA_VANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here

# News Data
NEWS_API_KEY=your_key_here

# Notifications (optional)
TELEGRAM_BOT_TOKEN=your_token_here
EMAIL_USERNAME=your_email@gmail.com
```

**Free API Key Sources:**
- [Alpha Vantage](https://www.alphavantage.co/support/#api-key) - 5 calls/minute free
- [NewsAPI](https://newsapi.org/register) - 1000 requests/day free
- [Finnhub](https://finnhub.io/register) - 60 calls/minute free

**Note:** The system works with free data sources (Yahoo Finance) if you don't add API keys.

### Step 5: Test the System

Run the system test:
```bash
source venv/bin/activate
python scripts/system_test.py
```

All tests should pass ✅. If any fail, check the error messages.

### Step 6: Generate Your First Brief

```bash
source venv/bin/activate
python scripts/generate_daily_brief.py
```

This will:
1. Analyze your portfolio
2. Fetch latest news
3. Run technical screening
4. Generate HTML, JSON, and Markdown reports
5. Open the HTML report in your browser

Check the `daily-briefs/` directory for output files.

## ⚙️ Configuration Options

### Portfolio Settings (`config/portfolio.json`)

Key sections to customize:

**Risk Management:**
```json
"risk_management": {
  "max_position_size": 0.05,        // 5% max per position
  "stop_loss_default": 0.15,        // 15% default stop loss
  "portfolio_stop_loss": 0.20,      // 20% total portfolio stop
  "cash_reserve_min": 0.10           // 10% minimum cash
}
```

**Alert Thresholds:**
```json
"portfolio_config": {
  "POSITION_LOSS_ALERT": -0.08,     // Alert at -8% single position
  "PORTFOLIO_LOSS_ALERT": -0.05,    // Alert at -5% total portfolio
  "MAX_SECTOR_WEIGHT": 0.40          // 40% max in any sector
}
```

### System Settings (`config/settings.py`)

**Market Data:**
- API rate limits
- Market hours
- Data refresh intervals

**News Analysis:**
- Sources to monitor
- Sentiment keywords
- Relevance scoring

**Technical Analysis:**
- Moving average periods
- RSI parameters
- Volume thresholds
- Screening criteria

## 🤖 Automation Setup

### Daily Execution (Cron Job)

To generate daily briefs automatically at 7:30 AM:

```bash
# Edit your crontab
crontab -e

# Add this line (update the path)
30 7 * * 1-5 cd /path/to/daily-investment-pipeline && ./venv/bin/python scripts/generate_daily_brief.py >> logs/cron.log 2>&1
```

### Portfolio Monitoring

For real-time portfolio monitoring during market hours:

```bash
# Monitor every hour during market hours (9 AM - 4 PM)
0 9-16 * * 1-5 cd /path/to/daily-investment-pipeline && ./venv/bin/python scripts/portfolio_monitor.py >> logs/monitor.log 2>&1
```

### Log Rotation

Set up log rotation to prevent disk space issues:

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/investment-pipeline

# Add this content:
/path/to/daily-investment-pipeline/logs/*.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
}
```

## 📊 Understanding the Output

### Daily Brief Components

**1. Executive Summary**
- Portfolio performance overview
- Market sentiment analysis
- Day's key metrics

**2. Critical Alerts**
- Stop loss triggers
- Position size warnings
- News-driven alerts

**3. Portfolio Positions**
- Current holdings and performance
- Daily changes and total returns
- Position sizes and allocation

**4. Technical Opportunities**
- Top-rated stocks from screening
- Entry/exit levels
- Risk/reward ratios

**5. News Analysis**
- Relevant news by sector
- Sentiment scoring
- Impact assessments

**6. Action Items**
- Immediate actions required
- Research priorities
- Risk management tasks

### File Outputs

- **HTML Brief**: Formatted report for easy reading
- **JSON Data**: Machine-readable for integrations
- **Markdown**: Text-based format for documentation
- **Raw Data**: Complete data snapshot for debugging

## 🔧 Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

**"No data retrieved" for stocks:**
- Check internet connection
- Verify stock symbols are correct
- Try different data source (yfinance vs API)

**Template not found:**
```bash
# Ensure you're in the right directory
pwd  # Should end with daily-investment-pipeline

# Check template exists
ls templates/daily_brief_template.html
```

**Portfolio file errors:**
- Validate JSON syntax: https://jsonlint.com/
- Check all required fields are present
- Ensure numeric values don't have quotes

### Performance Issues

**Slow data fetching:**
- Reduce number of stocks in screening
- Use API keys for faster data access
- Add delays between API calls if hitting rate limits

**Large output files:**
- Limit news articles in config
- Reduce historical data periods
- Enable log rotation

### Getting Help

**Check logs:**
```bash
# System errors
tail -f logs/pipeline.log

# Cron job issues
tail -f logs/cron.log

# Portfolio monitoring
tail -f logs/monitor.log
```

**Debug mode:**
```bash
# Run with extra output
python scripts/generate_daily_brief.py --verbose

# Test individual components
python scripts/news_analyzer.py
python scripts/technical_screener.py
python scripts/portfolio_monitor.py
```

## 📈 Customization

### Adding New Stocks

Edit `config/settings.py` to add stocks to screening:

```python
FOCUS_SECTORS = {
    'tech': {
        'tickers': ['NVDA', 'AMD', 'YOUR_STOCK_HERE'],
        'keywords': ['AI', 'semiconductor', 'your_keyword']
    }
}
```

### Custom Alerts

Modify `scripts/portfolio_monitor.py` to add custom alert logic:

```python
# Add in generate_position_alerts method
if your_custom_condition:
    alerts.append(PositionAlert(
        symbol=symbol,
        alert_type="custom_alert",
        severity="high",
        message="Your custom message",
        action_recommended="YOUR ACTION"
    ))
```

### New Data Sources

Add new news sources in `scripts/news_analyzer.py`:

```python
def _fetch_your_custom_source(self):
    # Your custom news fetching logic
    pass
```

## 🎯 Next Steps

1. **Week 1**: Run manually each morning to verify accuracy
2. **Week 2**: Set up automated cron job
3. **Week 3**: Add API keys for better data
4. **Week 4**: Customize alerts and thresholds
5. **Month 2**: Add custom integrations (email, Slack, etc.)

## 📞 Support

This system is designed to be self-contained and production-ready. The documentation covers most use cases, but you can:

1. Check the logs for error details
2. Run individual components to isolate issues
3. Use the system test script to verify setup
4. Customize settings based on your preferences

**Remember**: This system provides data and analysis, not financial advice. Always do your own research before making investment decisions.

---

🎉 **Congratulations!** You now have a professional-grade daily investment research pipeline. Tomorrow morning at 8:00 AM, you'll receive your first automated investment brief!