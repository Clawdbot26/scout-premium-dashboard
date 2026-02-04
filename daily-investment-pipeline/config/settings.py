#!/usr/bin/env python3
"""
Daily Investment Pipeline Configuration
Core settings for automated research system
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class MarketConfig:
    """Market data and timing configuration"""
    MARKET_OPEN = "09:30"
    MARKET_CLOSE = "16:00"
    TIMEZONE = "US/Eastern"
    TRADING_DAYS_LOOKBACK = 30
    
    # API rate limits
    API_CALLS_PER_MINUTE = 60
    NEWS_REFRESH_MINUTES = 15
    PORTFOLIO_CHECK_MINUTES = 5

@dataclass  
class SectorConfig:
    """Sector analysis configuration"""
    FOCUS_SECTORS = {
        'tech': {
            'keywords': ['AI', 'semiconductor', 'NVDA', 'ASML', 'chip', 'GPU'],
            'tickers': ['NVDA', 'AMD', 'ASML', 'TSM', 'INTC', 'QCOM'],
            'weight': 0.3  # 30% focus
        },
        'finance': {
            'keywords': ['fintech', 'payment', 'blockchain', 'crypto', 'DeFi'],
            'tickers': ['V', 'MA', 'PYPL', 'SQ', 'COIN', 'JPM'],
            'weight': 0.2
        },
        'healthcare': {
            'keywords': ['biotech', 'pharma', 'FDA', 'drug', 'clinical trial'],
            'tickers': ['JNJ', 'PFE', 'UNH', 'MRNA', 'GILD', 'BIIB'],
            'weight': 0.25
        },
        'energy': {
            'keywords': ['battery', 'EV', 'solar', 'wind', 'clean energy'],
            'tickers': ['TSLA', 'ENPH', 'SEDG', 'NEE', 'XOM', 'CVX'],
            'weight': 0.25
        }
    }

@dataclass
class TechnicalConfig:
    """Technical analysis parameters"""
    # Moving averages
    MA_SHORT = 20
    MA_MEDIUM = 50  
    MA_LONG = 200
    
    # RSI parameters
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    RSI_PERIOD = 14
    
    # Volume analysis
    VOLUME_SPIKE_THRESHOLD = 1.5  # 1.5x average volume
    VOLUME_LOOKBACK_DAYS = 20
    
    # Risk management
    MAX_POSITION_SIZE = 0.05  # 5% max per position
    STOP_LOSS_PCT = 0.15      # 15% stop loss
    MIN_RISK_REWARD = 2.0     # 2:1 minimum R:R
    
    # Screening criteria
    MIN_MARKET_CAP = 1_000_000_000  # $1B minimum
    MIN_DAILY_VOLUME = 1_000_000    # $1M daily volume
    MAX_PRICE = 1000  # Under $1000/share

@dataclass
class PortfolioConfig:
    """Portfolio monitoring configuration"""
    TOTAL_VALUE = 200_000  # $200k portfolio
    CASH_TARGET = 0.15     # 15% cash reserve
    MAX_SECTOR_WEIGHT = 0.4  # 40% max in any sector
    REBALANCE_THRESHOLD = 0.05  # 5% drift triggers rebalance alert
    
    # Alert thresholds
    POSITION_LOSS_ALERT = -0.08  # -8% single position alert
    PORTFOLIO_LOSS_ALERT = -0.05  # -5% total portfolio alert
    NEWS_IMPACT_THRESHOLD = 0.03  # 3% news-driven move

@dataclass
class NewsConfig:
    """News analysis configuration"""
    SOURCES = [
        'reuters', 'bloomberg', 'cnbc', 'marketwatch', 
        'seekingalpha', 'fool', 'benzinga'
    ]
    
    SENTIMENT_KEYWORDS = {
        'bullish': ['upgrade', 'beat', 'strong', 'growth', 'positive', 'outperform'],
        'bearish': ['downgrade', 'miss', 'weak', 'decline', 'negative', 'underperform'],
        'neutral': ['maintain', 'hold', 'inline', 'meets', 'as expected']
    }
    
    PRIORITY_TERMS = [
        'earnings', 'guidance', 'FDA approval', 'acquisition', 'partnership',
        'insider buying', 'analyst upgrade', 'breakthrough'
    ]

# System paths
DATA_DIR = "data"
OUTPUT_DIR = "daily-briefs"
TEMPLATE_DIR = "templates"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = "logs/pipeline.log"

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary"""
    return {
        'market': MarketConfig(),
        'sectors': SectorConfig(), 
        'technical': TechnicalConfig(),
        'portfolio': PortfolioConfig(),
        'news': NewsConfig()
    }

if __name__ == "__main__":
    config = get_config()
    print("Configuration loaded successfully:")
    for key, value in config.items():
        print(f"  {key}: {type(value).__name__}")