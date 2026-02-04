# Daily Investment Research Pipeline 🚀

## Overview
Comprehensive daily investment research system for Roni's ~$200k portfolio. Combines automated news analysis, technical screening, and portfolio monitoring into actionable 8 AM daily briefs.

## Quick Start
```bash
# Generate tomorrow's 8 AM brief
./scripts/generate_daily_brief.py

# Run portfolio health check
./scripts/portfolio_monitor.py

# Screen for new opportunities
./scripts/technical_screener.py
```

## Directory Structure
```
daily-investment-pipeline/
├── daily-briefs/           # Generated daily reports
├── sector-analysis/        # Sector-specific research
│   ├── tech/              # AI/Semiconductors
│   ├── finance/           # Fintech/Payment
│   ├── healthcare/        # Biotech
│   └── energy/            # Energy Transition
├── portfolio-tracking/    # Portfolio monitoring
├── news-analysis/         # Scraped and analyzed news
├── technical-screening/   # Stock screening results
├── templates/             # Report templates
├── scripts/              # Automation scripts
├── data/                 # Raw data storage
└── config/               # Configuration files
```

## Core Components
1. **News Analysis System** - Automated scraping for key sectors
2. **Technical Screening Framework** - Stock screening with indicators
3. **Portfolio Monitor** - Track positions and generate alerts
4. **Daily Brief Generator** - Combine all data into 8 AM reports

## Production Schedule
- **07:30 AM**: System runs automatically
- **08:00 AM**: Daily brief delivered
- **Market Open**: Real-time monitoring active
- **Market Close**: Performance summary

## Next Steps
1. Configure API keys in `config/credentials.env`
2. Set up portfolio positions in `config/portfolio.json`
3. Run initial system test: `./scripts/system_test.py`
4. Schedule cron job for daily execution

Built for scalability and extensibility.