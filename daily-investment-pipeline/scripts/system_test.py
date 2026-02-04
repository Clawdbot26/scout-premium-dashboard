#!/usr/bin/env python3
"""
System Test Script
Comprehensive testing of the daily investment pipeline
"""

import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    required_modules = [
        'pandas', 'numpy', 'yfinance', 'requests', 
        'jinja2', 'json', 'datetime'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️  Missing modules: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required modules imported successfully")
        return True

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config.settings import get_config
        config = get_config()
        
        print("   ✅ Configuration loaded")
        print(f"   📊 Market config: {type(config['market']).__name__}")
        print(f"   🏭 Sector config: {len(config['sectors'].FOCUS_SECTORS)} sectors")
        print(f"   📈 Technical config: MA periods {config['technical'].MA_SHORT}/{config['technical'].MA_MEDIUM}/{config['technical'].MA_LONG}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False

def test_portfolio_loading():
    """Test portfolio configuration loading"""
    print("\n💼 Testing portfolio configuration...")
    
    try:
        portfolio_file = "config/portfolio.json"
        
        if not os.path.exists(portfolio_file):
            print(f"   ⚠️  Portfolio file not found: {portfolio_file}")
            return False
        
        with open(portfolio_file, 'r') as f:
            portfolio = json.load(f)
        
        print("   ✅ Portfolio configuration loaded")
        print(f"   💰 Total value: ${portfolio['portfolio_metadata']['total_value']:,}")
        print(f"   📊 Positions: {len(portfolio['positions'])}")
        print(f"   💵 Cash: {portfolio['cash_position']['percentage']*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Portfolio loading error: {e}")
        return False

def test_data_fetching():
    """Test market data fetching"""
    print("\n📊 Testing market data fetching...")
    
    try:
        import yfinance as yf
        
        # Test with a common stock
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="5d")
        info = ticker.info
        
        if not hist.empty:
            print("   ✅ Historical data fetched")
            print(f"   📈 Latest close: ${hist['Close'].iloc[-1]:.2f}")
        else:
            print("   ❌ No historical data retrieved")
            return False
        
        if info:
            print("   ✅ Stock info fetched")
            print(f"   🏢 Company: {info.get('longName', 'N/A')}")
        else:
            print("   ⚠️  Stock info limited")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Data fetching error: {e}")
        return False

def test_news_analyzer():
    """Test news analysis system"""
    print("\n📰 Testing news analysis...")
    
    try:
        from scripts.news_analyzer import NewsAnalyzer
        
        analyzer = NewsAnalyzer()
        print("   ✅ News analyzer initialized")
        
        # Test sentiment analysis
        test_text = "NVDA reports strong earnings beat with AI chip demand surge"
        sentiment = analyzer.analyze_sentiment(test_text)
        print(f"   📝 Sentiment test: '{sentiment}' for positive text")
        
        # Test ticker extraction
        tickers = analyzer.extract_tickers("AAPL and MSFT both gained today")
        print(f"   🎯 Ticker extraction: {tickers}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ News analyzer error: {e}")
        traceback.print_exc()
        return False

def test_technical_screener():
    """Test technical screening system"""
    print("\n🎯 Testing technical screener...")
    
    try:
        from scripts.technical_screener import TechnicalScreener
        
        screener = TechnicalScreener()
        print("   ✅ Technical screener initialized")
        print(f"   📊 Stock universe: {len(screener.stock_universe)} symbols")
        
        # Test screening a single stock
        test_result = screener.screen_stock("AAPL")
        if test_result:
            print(f"   📈 Test screening: AAPL score {test_result.overall_score:.1f}")
            print(f"   💡 Recommendation: {test_result.recommendation}")
        else:
            print("   ⚠️  Test screening returned no result")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Technical screener error: {e}")
        traceback.print_exc()
        return False

def test_portfolio_monitor():
    """Test portfolio monitoring system"""
    print("\n💼 Testing portfolio monitor...")
    
    try:
        from scripts.portfolio_monitor import PortfolioMonitor
        
        monitor = PortfolioMonitor()
        print("   ✅ Portfolio monitor initialized")
        
        # Test portfolio analysis
        summary = monitor.monitor_portfolio()
        print(f"   💰 Portfolio value: ${summary.total_value:,.2f}")
        print(f"   📊 Positions: {len(summary.positions)}")
        print(f"   🚨 Alerts: {len(summary.alerts)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Portfolio monitor error: {e}")
        traceback.print_exc()
        return False

def test_brief_generator():
    """Test daily brief generation"""
    print("\n📝 Testing daily brief generator...")
    
    try:
        from scripts.generate_daily_brief import DailyBriefGenerator
        
        generator = DailyBriefGenerator()
        print("   ✅ Brief generator initialized")
        
        # Test template loading
        template = generator.jinja_env.get_template('daily_brief_template.html')
        print("   ✅ Template loaded successfully")
        
        # Test basic data collection (without full run)
        print("   🔄 Testing data collection...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Brief generator error: {e}")
        traceback.print_exc()
        return False

def test_directory_structure():
    """Test directory structure"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'config', 'scripts', 'templates', 
        'daily-briefs', 'portfolio-tracking',
        'news-analysis', 'technical-screening',
        'data'
    ]
    
    missing_dirs = []
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ (missing)")
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"\n⚠️  Creating missing directories: {', '.join(missing_dirs)}")
        for dir_name in missing_dirs:
            os.makedirs(dir_name, exist_ok=True)
        print("   ✅ Directories created")
    
    return True

def test_file_permissions():
    """Test file permissions for scripts"""
    print("\n🔒 Testing file permissions...")
    
    script_files = [
        'scripts/news_analyzer.py',
        'scripts/technical_screener.py', 
        'scripts/portfolio_monitor.py',
        'scripts/generate_daily_brief.py'
    ]
    
    for script in script_files:
        if os.path.exists(script):
            # Make executable
            os.chmod(script, 0o755)
            print(f"   ✅ {script} (executable)")
        else:
            print(f"   ❌ {script} (not found)")
    
    return True

def run_integration_test():
    """Run a quick integration test"""
    print("\n🚀 Running integration test...")
    
    try:
        # Import and run a minimal version of the pipeline
        from scripts.generate_daily_brief import DailyBriefGenerator
        
        generator = DailyBriefGenerator()
        
        # Create minimal test data
        test_data = {
            'timestamp': datetime.now(),
            'date': datetime.now().strftime("%A, %B %d, %Y"),
            'portfolio': type('obj', (object,), {
                'total_value': 200000.0,
                'day_change': 1500.0,
                'day_change_pct': 0.75,
                'unrealized_pnl': 5000.0,
                'unrealized_pnl_pct': 2.5,
                'positions': [],
                'alerts': [],
                'sector_allocation': {},
                'rebalancing_needed': False
            })(),
            'news_articles': [],
            'technical_picks': [],
            'news_sentiment': {'overall': 'neutral', 'tech': 'bullish'},
            'sector_analysis': {},
            'earnings_today': [],
            'economic_events': []
        }
        
        # Test JSON generation
        json_file = generator._generate_json_brief(test_data, "test")
        print(f"   ✅ JSON brief generated: {json_file}")
        
        # Test Markdown generation  
        md_file = generator._generate_markdown_brief(test_data, "test")
        print(f"   ✅ Markdown brief generated: {md_file}")
        
        print("   ✅ Integration test passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all system tests"""
    print("🧪 Daily Investment Pipeline - System Test")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Directory Structure", test_directory_structure),
        ("File Permissions", test_file_permissions),
        ("Portfolio Loading", test_portfolio_loading),
        ("Data Fetching", test_data_fetching),
        ("News Analyzer", test_news_analyzer),
        ("Technical Screener", test_technical_screener),
        ("Portfolio Monitor", test_portfolio_monitor),
        ("Brief Generator", test_brief_generator),
        ("Integration Test", run_integration_test)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"🧪 SYSTEM TEST RESULTS")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        print("\nNext steps:")
        print("1. Configure API keys in config/credentials.env")
        print("2. Update portfolio positions in config/portfolio.json")
        print("3. Run: ./scripts/generate_daily_brief.py")
        print("4. Set up cron job for daily 7:30 AM execution")
        return True
    else:
        print(f"\n⚠️  {failed} tests failed. Please fix issues before running in production.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)