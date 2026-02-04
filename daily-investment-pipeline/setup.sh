#!/bin/bash
# Daily Investment Pipeline Setup Script

echo "🚀 Setting up Daily Investment Pipeline..."
echo "=========================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "🐍 Python version: $PYTHON_VERSION"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "scripts" ]; then
    echo "❌ Please run this script from the daily-investment-pipeline directory"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📚 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Requirements installed successfully"
else
    echo "❌ Failed to install requirements"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p daily-briefs portfolio-tracking news-analysis technical-screening data logs

# Set up configuration files
echo "⚙️  Setting up configuration..."

# Copy credentials template if it doesn't exist
if [ ! -f "config/credentials.env" ]; then
    cp config/credentials.env.template config/credentials.env
    echo "✅ Created credentials.env (please fill in your API keys)"
else
    echo "✅ credentials.env already exists"
fi

# Make scripts executable
echo "🔒 Setting script permissions..."
chmod +x scripts/*.py
chmod +x setup.sh
echo "✅ Scripts are now executable"

# Run system test
echo "🧪 Running system tests..."
python3 scripts/system_test.py

if [ $? -eq 0 ]; then
    echo "✅ System tests passed"
else
    echo "⚠️  Some system tests failed - check output above"
fi

# Create sample cron job
echo "⏰ Creating sample cron job..."
cat > daily_pipeline_cron.txt << 'EOF'
# Daily Investment Pipeline - Add this to your crontab
# Run: crontab -e
# Then add this line:

# Generate daily brief at 7:30 AM ET Monday-Friday
30 7 * * 1-5 cd /path/to/daily-investment-pipeline && ./venv/bin/python scripts/generate_daily_brief.py >> logs/cron.log 2>&1

# Optional: Run portfolio monitor every hour during market hours
0 9-16 * * 1-5 cd /path/to/daily-investment-pipeline && ./venv/bin/python scripts/portfolio_monitor.py >> logs/monitor.log 2>&1
EOF

echo "✅ Sample cron job saved to daily_pipeline_cron.txt"

# Create logging configuration
echo "📝 Setting up logging..."
cat > logs/README.md << 'EOF'
# Logs Directory

This directory contains log files from the daily investment pipeline:

- `pipeline.log` - Main pipeline execution logs
- `cron.log` - Cron job execution logs  
- `monitor.log` - Portfolio monitoring logs
- `system_test.log` - System test results

Log files are automatically rotated to prevent disk space issues.
EOF

echo "✅ Logging configured"

# Summary and next steps
echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "Next Steps:"
echo "1. 📝 Edit config/credentials.env and add your API keys"
echo "2. 💼 Update config/portfolio.json with your actual positions"
echo "3. 🧪 Run a test: ./venv/bin/python scripts/generate_daily_brief.py"
echo "4. ⏰ Set up cron job using daily_pipeline_cron.txt as reference"
echo "5. 📊 Daily briefs will be generated in daily-briefs/ directory"
echo ""
echo "🔗 API Keys Needed (optional but recommended):"
echo "   - Alpha Vantage: https://www.alphavantage.co/support/#api-key"
echo "   - NewsAPI: https://newsapi.org/register"
echo "   - Finnhub: https://finnhub.io/register"
echo ""
echo "💡 Free alternatives work too (Yahoo Finance, RSS feeds)"
echo ""
echo "📚 Documentation: See README.md for detailed usage instructions"
echo ""
echo "⚡ Quick start test:"
echo "   source venv/bin/activate"
echo "   python scripts/generate_daily_brief.py"