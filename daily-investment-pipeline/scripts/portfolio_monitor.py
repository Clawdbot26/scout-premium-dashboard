#!/usr/bin/env python3
"""
Portfolio Monitor Setup
Framework to track portfolio positions and generate alerts
"""

import yfinance as yf
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np

# Add parent directory to path for config imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.settings import get_config

@dataclass
class PositionAlert:
    symbol: str
    alert_type: str  # stop_loss, profit_target, news_impact, rebalance
    severity: str    # low, medium, high, critical
    message: str
    current_price: float
    trigger_price: float
    action_recommended: str
    timestamp: str

@dataclass
class PositionPerformance:
    symbol: str
    shares: float
    avg_cost: float
    current_price: float
    current_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    day_change: float
    day_change_pct: float
    position_size_pct: float
    days_held: int
    stop_loss_price: float
    target_price: float
    risk_reward_ratio: float

@dataclass
class PortfolioSummary:
    total_value: float
    cash_position: float
    invested_amount: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    day_change: float
    day_change_pct: float
    ytd_return: float
    positions: List[PositionPerformance]
    alerts: List[PositionAlert]
    sector_allocation: Dict[str, float]
    risk_metrics: Dict[str, float]
    rebalancing_needed: bool

class PortfolioMonitor:
    def __init__(self, portfolio_file: str = "config/portfolio.json"):
        self.config = get_config()
        self.portfolio_config = self.config['portfolio']
        self.portfolio_file = portfolio_file
        self.portfolio_data = self._load_portfolio()
        
    def _load_portfolio(self) -> Dict:
        """Load portfolio configuration from JSON file"""
        try:
            with open(self.portfolio_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Portfolio file not found: {self.portfolio_file}")
            return self._create_default_portfolio()
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            return self._create_default_portfolio()
    
    def _create_default_portfolio(self) -> Dict:
        """Create a default portfolio structure"""
        return {
            "portfolio_metadata": {
                "total_value": 200000,
                "last_updated": datetime.now().isoformat(),
                "currency": "USD"
            },
            "positions": [],
            "cash_position": {"amount": 200000, "percentage": 1.0},
            "sector_allocation": {},
            "risk_management": {
                "max_position_size": 0.05,
                "stop_loss_default": 0.15,
                "portfolio_stop_loss": 0.20
            }
        }
    
    def get_current_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch current prices and daily changes for symbols"""
        if not symbols:
            return {}
        
        try:
            # Create space-separated string for yfinance
            tickers_str = ' '.join(symbols)
            tickers = yf.Tickers(tickers_str)
            
            prices = {}
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="5d")
                    info = ticker.info
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                        
                        prices[symbol] = {
                            'current_price': current_price,
                            'previous_close': prev_close,
                            'day_change': current_price - prev_close,
                            'day_change_pct': (current_price - prev_close) / prev_close * 100,
                            'volume': hist['Volume'].iloc[-1],
                            'market_cap': info.get('marketCap', 0),
                            'company_name': info.get('longName', symbol)
                        }
                except Exception as e:
                    print(f"Error fetching data for {symbol}: {e}")
                    continue
            
            return prices
            
        except Exception as e:
            print(f"Error fetching price data: {e}")
            return {}
    
    def calculate_position_performance(self, position: Dict, current_prices: Dict) -> PositionPerformance:
        """Calculate performance metrics for a single position"""
        symbol = position['symbol']
        shares = position['shares']
        avg_cost = position['avg_cost']
        
        if symbol not in current_prices:
            # Use last known price or avg_cost as fallback
            current_price = avg_cost
            day_change = 0
            day_change_pct = 0
        else:
            price_data = current_prices[symbol]
            current_price = price_data['current_price']
            day_change = price_data['day_change'] * shares
            day_change_pct = price_data['day_change_pct']
        
        # Calculate metrics
        current_value = shares * current_price
        cost_basis = shares * avg_cost
        unrealized_pnl = current_value - cost_basis
        unrealized_pnl_pct = (unrealized_pnl / cost_basis) * 100 if cost_basis > 0 else 0
        
        # Portfolio percentage
        portfolio_total = self.portfolio_data['portfolio_metadata']['total_value']
        position_size_pct = (current_value / portfolio_total) * 100
        
        # Days held calculation
        entry_date = datetime.fromisoformat(position.get('entry_date', datetime.now().isoformat()))
        days_held = (datetime.now() - entry_date).days
        
        # Risk metrics
        stop_loss_price = position.get('stop_loss', avg_cost * 0.85)  # Default 15% stop
        target_price = position.get('target_price', avg_cost * 1.25)   # Default 25% target
        
        # Risk/reward calculation
        risk = current_price - stop_loss_price
        reward = target_price - current_price
        risk_reward_ratio = (reward / risk) if risk > 0 else 0
        
        return PositionPerformance(
            symbol=symbol,
            shares=shares,
            avg_cost=avg_cost,
            current_price=current_price,
            current_value=current_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_pct=unrealized_pnl_pct,
            day_change=day_change,
            day_change_pct=day_change_pct,
            position_size_pct=position_size_pct,
            days_held=days_held,
            stop_loss_price=stop_loss_price,
            target_price=target_price,
            risk_reward_ratio=risk_reward_ratio
        )
    
    def generate_position_alerts(self, position: PositionPerformance) -> List[PositionAlert]:
        """Generate alerts for individual positions"""
        alerts = []
        timestamp = datetime.now().isoformat()
        
        # Stop loss alert
        if position.current_price <= position.stop_loss_price:
            alerts.append(PositionAlert(
                symbol=position.symbol,
                alert_type="stop_loss",
                severity="critical",
                message=f"Price ${position.current_price:.2f} hit stop loss ${position.stop_loss_price:.2f}",
                current_price=position.current_price,
                trigger_price=position.stop_loss_price,
                action_recommended="SELL IMMEDIATELY",
                timestamp=timestamp
            ))
        
        # Near stop loss warning
        elif position.current_price <= position.stop_loss_price * 1.05:  # Within 5% of stop
            alerts.append(PositionAlert(
                symbol=position.symbol,
                alert_type="stop_loss",
                severity="high",
                message=f"Price ${position.current_price:.2f} approaching stop loss ${position.stop_loss_price:.2f}",
                current_price=position.current_price,
                trigger_price=position.stop_loss_price,
                action_recommended="MONITOR CLOSELY",
                timestamp=timestamp
            ))
        
        # Profit target alert
        if position.current_price >= position.target_price:
            alerts.append(PositionAlert(
                symbol=position.symbol,
                alert_type="profit_target",
                severity="medium",
                message=f"Price ${position.current_price:.2f} hit target ${position.target_price:.2f}",
                current_price=position.current_price,
                trigger_price=position.target_price,
                action_recommended="CONSIDER TAKING PROFITS",
                timestamp=timestamp
            ))
        
        # Large single-day loss
        if position.unrealized_pnl_pct <= self.portfolio_config.POSITION_LOSS_ALERT * 100:
            alerts.append(PositionAlert(
                symbol=position.symbol,
                alert_type="large_loss",
                severity="high",
                message=f"Position down {position.unrealized_pnl_pct:.1f}% (${position.unrealized_pnl:.0f})",
                current_price=position.current_price,
                trigger_price=position.avg_cost,
                action_recommended="REVIEW POSITION",
                timestamp=timestamp
            ))
        
        # Position size too large
        if position.position_size_pct > self.portfolio_config.MAX_POSITION_SIZE * 100:
            alerts.append(PositionAlert(
                symbol=position.symbol,
                alert_type="position_size",
                severity="medium",
                message=f"Position size {position.position_size_pct:.1f}% exceeds max {self.portfolio_config.MAX_POSITION_SIZE*100:.1f}%",
                current_price=position.current_price,
                trigger_price=0,
                action_recommended="CONSIDER TRIMMING",
                timestamp=timestamp
            ))
        
        return alerts
    
    def calculate_sector_allocation(self, positions: List[PositionPerformance]) -> Dict[str, float]:
        """Calculate current sector allocation"""
        sector_values = {}
        total_invested = sum(pos.current_value for pos in positions)
        
        # Map symbols to sectors (from config)
        symbol_to_sector = {}
        for sector, sector_data in self.config['sectors'].FOCUS_SECTORS.items():
            for ticker in sector_data['tickers']:
                symbol_to_sector[ticker] = sector
        
        for position in positions:
            sector = symbol_to_sector.get(position.symbol, 'other')
            if sector not in sector_values:
                sector_values[sector] = 0
            sector_values[sector] += position.current_value
        
        # Convert to percentages
        if total_invested > 0:
            sector_allocation = {sector: (value / total_invested) * 100 
                              for sector, value in sector_values.items()}
        else:
            sector_allocation = {}
        
        return sector_allocation
    
    def calculate_risk_metrics(self, positions: List[PositionPerformance]) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        if not positions:
            return {}
        
        # Portfolio beta (simplified - assumes market beta of 1.0 for all stocks)
        weights = [pos.current_value for pos in positions]
        total_value = sum(weights)
        weights = [w / total_value for w in weights]
        
        # Concentration risk (largest position percentage)
        max_position = max((pos.position_size_pct for pos in positions), default=0)
        
        # Stop loss risk (percentage of portfolio at risk)
        total_risk = sum(max(0, pos.current_value - (pos.shares * pos.stop_loss_price)) 
                        for pos in positions)
        risk_percentage = (total_risk / total_value) * 100 if total_value > 0 else 0
        
        # Diversification score (number of positions / concentration)
        num_positions = len(positions)
        diversification_score = min(num_positions / max_position * 20, 100) if max_position > 0 else 0
        
        return {
            'max_position_size': max_position,
            'num_positions': num_positions,
            'portfolio_risk_pct': risk_percentage,
            'diversification_score': diversification_score,
            'estimated_beta': 1.0  # Simplified assumption
        }
    
    def monitor_portfolio(self) -> PortfolioSummary:
        """Main portfolio monitoring function"""
        positions_data = self.portfolio_data.get('positions', [])
        cash_data = self.portfolio_data.get('cash_position', {})
        
        if not positions_data:
            print("No positions found in portfolio")
            return PortfolioSummary(
                total_value=cash_data.get('amount', 0),
                cash_position=cash_data.get('amount', 0),
                invested_amount=0,
                unrealized_pnl=0,
                unrealized_pnl_pct=0,
                day_change=0,
                day_change_pct=0,
                ytd_return=0,
                positions=[],
                alerts=[],
                sector_allocation={},
                risk_metrics={},
                rebalancing_needed=False
            )
        
        # Get symbols and fetch prices
        symbols = [pos['symbol'] for pos in positions_data]
        current_prices = self.get_current_prices(symbols)
        
        # Calculate performance for each position
        position_performances = []
        all_alerts = []
        
        for pos_data in positions_data:
            perf = self.calculate_position_performance(pos_data, current_prices)
            position_performances.append(perf)
            
            # Generate alerts for this position
            alerts = self.generate_position_alerts(perf)
            all_alerts.extend(alerts)
        
        # Calculate portfolio totals
        cash_amount = cash_data.get('amount', 0)
        invested_amount = sum(pos.current_value for pos in position_performances)
        total_value = cash_amount + invested_amount
        
        # Portfolio P&L
        cost_basis = sum(pos.shares * pos.avg_cost for pos in position_performances)
        unrealized_pnl = invested_amount - cost_basis
        unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
        
        # Daily change
        day_change = sum(pos.day_change for pos in position_performances)
        day_change_pct = (day_change / (total_value - day_change) * 100) if total_value > day_change else 0
        
        # Calculate allocations and risk metrics
        sector_allocation = self.calculate_sector_allocation(position_performances)
        risk_metrics = self.calculate_risk_metrics(position_performances)
        
        # Check if rebalancing needed
        rebalancing_needed = self._check_rebalancing_needed(sector_allocation, position_performances)
        
        # Generate portfolio-level alerts
        portfolio_alerts = self._generate_portfolio_alerts(
            unrealized_pnl_pct, sector_allocation, position_performances
        )
        all_alerts.extend(portfolio_alerts)
        
        return PortfolioSummary(
            total_value=total_value,
            cash_position=cash_amount,
            invested_amount=invested_amount,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_pct=unrealized_pnl_pct,
            day_change=day_change,
            day_change_pct=day_change_pct,
            ytd_return=0,  # TODO: Calculate YTD return
            positions=position_performances,
            alerts=all_alerts,
            sector_allocation=sector_allocation,
            risk_metrics=risk_metrics,
            rebalancing_needed=rebalancing_needed
        )
    
    def _check_rebalancing_needed(self, sector_allocation: Dict[str, float], 
                                positions: List[PositionPerformance]) -> bool:
        """Check if portfolio rebalancing is needed"""
        # Check sector concentration
        for sector, allocation in sector_allocation.items():
            if allocation > self.portfolio_config.MAX_SECTOR_WEIGHT * 100:
                return True
        
        # Check position sizes
        for pos in positions:
            if pos.position_size_pct > self.portfolio_config.MAX_POSITION_SIZE * 100:
                return True
        
        return False
    
    def _generate_portfolio_alerts(self, unrealized_pnl_pct: float, 
                                 sector_allocation: Dict[str, float],
                                 positions: List[PositionPerformance]) -> List[PositionAlert]:
        """Generate portfolio-level alerts"""
        alerts = []
        timestamp = datetime.now().isoformat()
        
        # Portfolio loss alert
        if unrealized_pnl_pct <= self.portfolio_config.PORTFOLIO_LOSS_ALERT * 100:
            alerts.append(PositionAlert(
                symbol="PORTFOLIO",
                alert_type="portfolio_loss",
                severity="critical",
                message=f"Portfolio down {unrealized_pnl_pct:.1f}%",
                current_price=0,
                trigger_price=0,
                action_recommended="REVIEW ALL POSITIONS",
                timestamp=timestamp
            ))
        
        # Sector concentration alerts
        for sector, allocation in sector_allocation.items():
            if allocation > self.portfolio_config.MAX_SECTOR_WEIGHT * 100:
                alerts.append(PositionAlert(
                    symbol="PORTFOLIO",
                    alert_type="sector_concentration",
                    severity="medium",
                    message=f"{sector.upper()} sector at {allocation:.1f}% (max: {self.portfolio_config.MAX_SECTOR_WEIGHT*100:.1f}%)",
                    current_price=0,
                    trigger_price=0,
                    action_recommended="REBALANCE SECTOR ALLOCATION",
                    timestamp=timestamp
                ))
        
        # Cash level alerts
        total_value = sum(pos.current_value for pos in positions)
        cash_pct = self.portfolio_data.get('cash_position', {}).get('percentage', 0) * 100
        
        if cash_pct < self.portfolio_config.CASH_TARGET * 100 * 0.5:  # Less than half target
            alerts.append(PositionAlert(
                symbol="PORTFOLIO",
                alert_type="low_cash",
                severity="low",
                message=f"Cash level {cash_pct:.1f}% below target {self.portfolio_config.CASH_TARGET*100:.1f}%",
                current_price=0,
                trigger_price=0,
                action_recommended="CONSIDER RAISING CASH",
                timestamp=timestamp
            ))
        
        return alerts
    
    def save_monitoring_results(self, summary: PortfolioSummary, 
                              output_dir: str = "portfolio-tracking") -> str:
        """Save portfolio monitoring results to JSON file"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{output_dir}/portfolio_monitor_{timestamp}.json"
        
        # Convert to dict for JSON serialization
        output = {
            'timestamp': datetime.now().isoformat(),
            'summary': asdict(summary),
            'alerts_by_severity': {
                'critical': len([a for a in summary.alerts if a.severity == 'critical']),
                'high': len([a for a in summary.alerts if a.severity == 'high']),
                'medium': len([a for a in summary.alerts if a.severity == 'medium']),
                'low': len([a for a in summary.alerts if a.severity == 'low'])
            }
        }
        
        # Convert dataclasses in summary to dicts
        output['summary']['positions'] = [asdict(pos) for pos in summary.positions]
        output['summary']['alerts'] = [asdict(alert) for alert in summary.alerts]
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"Portfolio monitoring results saved to: {filename}")
        return filename
    
    def print_portfolio_summary(self, summary: PortfolioSummary):
        """Print formatted portfolio summary"""
        print(f"\n{'='*60}")
        print(f"📊 PORTFOLIO SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}")
        
        print(f"\n💰 PORTFOLIO VALUE")
        print(f"Total Value:     ${summary.total_value:12,.2f}")
        print(f"Cash Position:   ${summary.cash_position:12,.2f}")
        print(f"Invested:        ${summary.invested_amount:12,.2f}")
        print(f"Unrealized P&L:  ${summary.unrealized_pnl:12,.2f} ({summary.unrealized_pnl_pct:+5.1f}%)")
        print(f"Day Change:      ${summary.day_change:12,.2f} ({summary.day_change_pct:+5.1f}%)")
        
        print(f"\n📈 TOP POSITIONS")
        for i, pos in enumerate(summary.positions[:5], 1):
            print(f"{i}. {pos.symbol:5s} ${pos.current_price:8.2f} "
                  f"${pos.unrealized_pnl:8,.0f} ({pos.unrealized_pnl_pct:+5.1f}%) "
                  f"{pos.position_size_pct:4.1f}%")
        
        print(f"\n🎯 SECTOR ALLOCATION")
        for sector, allocation in sorted(summary.sector_allocation.items(), 
                                       key=lambda x: x[1], reverse=True):
            print(f"{sector.capitalize():12s}: {allocation:5.1f}%")
        
        if summary.alerts:
            print(f"\n🚨 ACTIVE ALERTS ({len(summary.alerts)})")
            critical_alerts = [a for a in summary.alerts if a.severity == 'critical']
            high_alerts = [a for a in summary.alerts if a.severity == 'high']
            
            for alert in critical_alerts + high_alerts:
                severity_emoji = "🔴" if alert.severity == "critical" else "🟡"
                print(f"{severity_emoji} {alert.symbol}: {alert.message}")
                print(f"   Action: {alert.action_recommended}")
        
        if summary.rebalancing_needed:
            print(f"\n⚖️ REBALANCING RECOMMENDED")
            print(f"Portfolio allocation is outside target ranges")

def main():
    """Main execution function"""
    print("📊 Starting Portfolio Monitor...")
    
    monitor = PortfolioMonitor()
    
    # Run monitoring
    summary = monitor.monitor_portfolio()
    
    # Save results
    output_file = monitor.save_monitoring_results(summary)
    
    # Print summary
    monitor.print_portfolio_summary(summary)
    
    print(f"\n💾 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    main()