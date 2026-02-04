#!/usr/bin/env python3
"""
Technical Screening Framework
Stock screening system based on technical indicators and fundamentals
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add parent directory to path for config imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.settings import get_config

@dataclass
class TechnicalSignal:
    indicator: str
    value: float
    signal: str  # bullish, bearish, neutral
    strength: float  # 0-100
    description: str

@dataclass
class ScreenResult:
    symbol: str
    company_name: str
    sector: str
    price: float
    market_cap: float
    volume: float
    signals: List[TechnicalSignal]
    overall_score: float
    risk_reward_ratio: float
    recommendation: str  # strong_buy, buy, hold, sell, strong_sell
    entry_price: Optional[float]
    stop_loss: Optional[float]
    target_price: Optional[float]
    notes: List[str]

class TechnicalScreener:
    def __init__(self):
        self.config = get_config()
        self.tech_config = self.config['technical']
        self.sector_config = self.config['sectors']
        
        # Build universe of stocks to screen
        self.stock_universe = self._build_stock_universe()
        
    def _build_stock_universe(self) -> List[str]:
        """Build universe of stocks to screen from sector configurations"""
        universe = []
        for sector_data in self.sector_config.FOCUS_SECTORS.values():
            universe.extend(sector_data['tickers'])
        
        # Add some additional high-quality stocks
        additional_stocks = [
            'AAPL', 'GOOGL', 'AMZN', 'META', 'BRK-B',
            'JNJ', 'PG', 'KO', 'WMT', 'HD'
        ]
        universe.extend(additional_stocks)
        
        # Remove duplicates
        return list(set(universe))
    
    def fetch_stock_data(self, symbol: str, period: str = "6mo") -> Optional[pd.DataFrame]:
        """Fetch historical stock data"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            
            if hist.empty:
                return None
                
            # Add volume dollar amount
            hist['Volume_Dollar'] = hist['Close'] * hist['Volume']
            
            return hist
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def fetch_stock_info(self, symbol: str) -> Dict:
        """Fetch stock information and fundamentals"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return info
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return {}
    
    def calculate_moving_averages(self, data: pd.DataFrame) -> Dict[str, TechnicalSignal]:
        """Calculate moving average signals"""
        signals = {}
        
        if len(data) < self.tech_config.MA_LONG:
            return signals
        
        # Calculate MAs
        ma20 = data['Close'].rolling(window=self.tech_config.MA_SHORT).mean()
        ma50 = data['Close'].rolling(window=self.tech_config.MA_MEDIUM).mean()
        ma200 = data['Close'].rolling(window=self.tech_config.MA_LONG).mean()
        
        current_price = data['Close'].iloc[-1]
        current_ma20 = ma20.iloc[-1]
        current_ma50 = ma50.iloc[-1]
        current_ma200 = ma200.iloc[-1]
        
        # MA20 Signal
        ma20_signal = "bullish" if current_price > current_ma20 else "bearish"
        ma20_strength = min(abs(current_price - current_ma20) / current_ma20 * 100, 100)
        
        signals['ma20'] = TechnicalSignal(
            indicator="MA20",
            value=current_ma20,
            signal=ma20_signal,
            strength=ma20_strength,
            description=f"Price {'above' if ma20_signal == 'bullish' else 'below'} 20-day MA"
        )
        
        # MA50 Signal
        ma50_signal = "bullish" if current_price > current_ma50 else "bearish"
        ma50_strength = min(abs(current_price - current_ma50) / current_ma50 * 100, 100)
        
        signals['ma50'] = TechnicalSignal(
            indicator="MA50",
            value=current_ma50,
            signal=ma50_signal,
            strength=ma50_strength,
            description=f"Price {'above' if ma50_signal == 'bullish' else 'below'} 50-day MA"
        )
        
        # MA200 Signal (most important)
        ma200_signal = "bullish" if current_price > current_ma200 else "bearish"
        ma200_strength = min(abs(current_price - current_ma200) / current_ma200 * 100, 100)
        
        signals['ma200'] = TechnicalSignal(
            indicator="MA200",
            value=current_ma200,
            signal=ma200_signal,
            strength=ma200_strength,
            description=f"Price {'above' if ma200_signal == 'bullish' else 'below'} 200-day MA"
        )
        
        return signals
    
    def calculate_rsi(self, data: pd.DataFrame) -> Optional[TechnicalSignal]:
        """Calculate RSI signal"""
        if len(data) < self.tech_config.RSI_PERIOD + 1:
            return None
        
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.tech_config.RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.tech_config.RSI_PERIOD).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        if current_rsi <= self.tech_config.RSI_OVERSOLD:
            signal = "bullish"
            strength = (self.tech_config.RSI_OVERSOLD - current_rsi) * 2
            description = f"RSI oversold at {current_rsi:.1f}"
        elif current_rsi >= self.tech_config.RSI_OVERBOUGHT:
            signal = "bearish"
            strength = (current_rsi - self.tech_config.RSI_OVERBOUGHT) * 2
            description = f"RSI overbought at {current_rsi:.1f}"
        else:
            signal = "neutral"
            strength = 50 - abs(50 - current_rsi)
            description = f"RSI neutral at {current_rsi:.1f}"
        
        return TechnicalSignal(
            indicator="RSI",
            value=current_rsi,
            signal=signal,
            strength=min(strength, 100),
            description=description
        )
    
    def calculate_volume_signal(self, data: pd.DataFrame) -> Optional[TechnicalSignal]:
        """Calculate volume-based signal"""
        if len(data) < self.tech_config.VOLUME_LOOKBACK_DAYS:
            return None
        
        avg_volume = data['Volume'].rolling(
            window=self.tech_config.VOLUME_LOOKBACK_DAYS
        ).mean()
        
        current_volume = data['Volume'].iloc[-1]
        avg_volume_current = avg_volume.iloc[-1]
        
        volume_ratio = current_volume / avg_volume_current
        
        if volume_ratio >= self.tech_config.VOLUME_SPIKE_THRESHOLD:
            signal = "bullish"
            strength = min(volume_ratio * 30, 100)
            description = f"Volume spike: {volume_ratio:.1f}x average"
        else:
            signal = "neutral"
            strength = max(100 - (volume_ratio * 50), 20)
            description = f"Volume: {volume_ratio:.1f}x average"
        
        return TechnicalSignal(
            indicator="Volume",
            value=current_volume,
            signal=signal,
            strength=strength,
            description=description
        )
    
    def calculate_price_momentum(self, data: pd.DataFrame) -> Optional[TechnicalSignal]:
        """Calculate price momentum signal"""
        if len(data) < 20:
            return None
        
        # Price change over different periods
        price_change_5d = (data['Close'].iloc[-1] - data['Close'].iloc[-6]) / data['Close'].iloc[-6]
        price_change_20d = (data['Close'].iloc[-1] - data['Close'].iloc[-21]) / data['Close'].iloc[-21]
        
        momentum_score = (price_change_5d * 0.6) + (price_change_20d * 0.4)
        
        if momentum_score > 0.05:  # 5% positive momentum
            signal = "bullish"
            strength = min(momentum_score * 500, 100)
            description = f"Strong upward momentum: {momentum_score*100:.1f}%"
        elif momentum_score < -0.05:  # 5% negative momentum
            signal = "bearish"
            strength = min(abs(momentum_score) * 500, 100)
            description = f"Downward momentum: {momentum_score*100:.1f}%"
        else:
            signal = "neutral"
            strength = 50
            description = f"Sideways momentum: {momentum_score*100:.1f}%"
        
        return TechnicalSignal(
            indicator="Momentum",
            value=momentum_score * 100,
            signal=signal,
            strength=strength,
            description=description
        )
    
    def calculate_support_resistance(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate support and resistance levels"""
        if len(data) < 50:
            return {}
        
        # Simple approach: use recent highs/lows
        recent_data = data.tail(50)
        
        # Find local maxima and minima
        highs = recent_data['High'].rolling(window=5, center=True).max()
        lows = recent_data['Low'].rolling(window=5, center=True).min()
        
        resistance = recent_data[recent_data['High'] == highs]['High'].max()
        support = recent_data[recent_data['Low'] == lows]['Low'].min()
        
        current_price = data['Close'].iloc[-1]
        
        return {
            'support': support,
            'resistance': resistance,
            'distance_to_support': (current_price - support) / current_price,
            'distance_to_resistance': (resistance - current_price) / current_price
        }
    
    def screen_stock(self, symbol: str) -> Optional[ScreenResult]:
        """Screen individual stock and return analysis"""
        try:
            print(f"Screening {symbol}...")
            
            # Fetch data
            data = self.fetch_stock_data(symbol)
            info = self.fetch_stock_info(symbol)
            
            if data is None or data.empty:
                return None
            
            # Basic filtering
            current_price = data['Close'].iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            market_cap = info.get('marketCap', 0)
            
            # Apply filters from config
            if market_cap < self.tech_config.MIN_MARKET_CAP:
                return None
            if current_price > self.tech_config.MAX_PRICE:
                return None
            if current_volume < self.tech_config.MIN_DAILY_VOLUME:
                return None
            
            # Calculate signals
            signals = []
            
            # Moving average signals
            ma_signals = self.calculate_moving_averages(data)
            signals.extend(ma_signals.values())
            
            # RSI signal
            rsi_signal = self.calculate_rsi(data)
            if rsi_signal:
                signals.append(rsi_signal)
            
            # Volume signal
            volume_signal = self.calculate_volume_signal(data)
            if volume_signal:
                signals.append(volume_signal)
            
            # Momentum signal
            momentum_signal = self.calculate_price_momentum(data)
            if momentum_signal:
                signals.append(momentum_signal)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(signals)
            
            # Calculate support/resistance
            sr_levels = self.calculate_support_resistance(data)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(overall_score, signals)
            
            # Calculate entry/exit levels
            entry_price, stop_loss, target_price = self._calculate_entry_exit_levels(
                current_price, sr_levels, overall_score
            )
            
            # Risk/reward ratio
            risk_reward = self._calculate_risk_reward(current_price, stop_loss, target_price)
            
            # Determine sector
            sector = self._determine_sector(symbol)
            
            # Generate notes
            notes = self._generate_notes(signals, sr_levels, info)
            
            return ScreenResult(
                symbol=symbol,
                company_name=info.get('longName', symbol),
                sector=sector,
                price=current_price,
                market_cap=market_cap,
                volume=current_volume,
                signals=signals,
                overall_score=overall_score,
                risk_reward_ratio=risk_reward,
                recommendation=recommendation,
                entry_price=entry_price,
                stop_loss=stop_loss,
                target_price=target_price,
                notes=notes
            )
            
        except Exception as e:
            print(f"Error screening {symbol}: {e}")
            return None
    
    def _calculate_overall_score(self, signals: List[TechnicalSignal]) -> float:
        """Calculate overall technical score from signals"""
        if not signals:
            return 0
        
        score = 0
        weights = {
            'MA200': 0.25,  # Most important
            'MA50': 0.20,
            'MA20': 0.15,
            'RSI': 0.15,
            'Volume': 0.15,
            'Momentum': 0.10
        }
        
        for signal in signals:
            weight = weights.get(signal.indicator, 0.1)
            
            if signal.signal == "bullish":
                signal_score = signal.strength
            elif signal.signal == "bearish":
                signal_score = -signal.strength
            else:  # neutral
                signal_score = 0
            
            score += signal_score * weight
        
        # Normalize to 0-100
        return max(min(score + 50, 100), 0)
    
    def _generate_recommendation(self, overall_score: float, signals: List[TechnicalSignal]) -> str:
        """Generate buy/sell recommendation"""
        # Check for disqualifying factors
        ma200_signal = next((s for s in signals if s.indicator == "MA200"), None)
        if ma200_signal and ma200_signal.signal == "bearish":
            if overall_score < 40:
                return "sell"
        
        # Generate recommendation based on score
        if overall_score >= 80:
            return "strong_buy"
        elif overall_score >= 65:
            return "buy"
        elif overall_score >= 35:
            return "hold"
        elif overall_score >= 20:
            return "sell"
        else:
            return "strong_sell"
    
    def _calculate_entry_exit_levels(self, current_price: float, sr_levels: Dict, score: float) -> tuple:
        """Calculate entry, stop loss, and target prices"""
        # Entry price (slightly below current for better entry)
        entry_price = current_price * 0.99  # 1% below current
        
        # Stop loss
        if 'support' in sr_levels and sr_levels['support']:
            # Use support level or 15% below entry, whichever is closer
            support_stop = sr_levels['support'] * 0.98  # 2% below support
            percentage_stop = entry_price * (1 - self.tech_config.STOP_LOSS_PCT)
            stop_loss = max(support_stop, percentage_stop)
        else:
            stop_loss = entry_price * (1 - self.tech_config.STOP_LOSS_PCT)
        
        # Target price
        if 'resistance' in sr_levels and sr_levels['resistance']:
            resistance_target = sr_levels['resistance'] * 0.98  # Slightly below resistance
        else:
            resistance_target = None
        
        # Calculate target based on risk-reward ratio
        risk = entry_price - stop_loss
        min_target = entry_price + (risk * self.tech_config.MIN_RISK_REWARD)
        
        if resistance_target and resistance_target > min_target:
            target_price = resistance_target
        else:
            target_price = min_target
        
        return entry_price, stop_loss, target_price
    
    def _calculate_risk_reward(self, current_price: float, stop_loss: Optional[float], 
                             target_price: Optional[float]) -> float:
        """Calculate risk/reward ratio"""
        if not stop_loss or not target_price:
            return 0
        
        risk = current_price - stop_loss
        reward = target_price - current_price
        
        if risk <= 0:
            return 0
        
        return reward / risk
    
    def _determine_sector(self, symbol: str) -> str:
        """Determine which sector this stock belongs to"""
        for sector, sector_data in self.sector_config.FOCUS_SECTORS.items():
            if symbol in sector_data['tickers']:
                return sector
        return "other"
    
    def _generate_notes(self, signals: List[TechnicalSignal], sr_levels: Dict, info: Dict) -> List[str]:
        """Generate analysis notes"""
        notes = []
        
        # Signal-based notes
        strong_signals = [s for s in signals if s.strength > 70]
        if strong_signals:
            notes.append(f"Strong signals: {', '.join([s.indicator for s in strong_signals])}")
        
        # Support/resistance notes
        if sr_levels:
            notes.append(f"Support: ${sr_levels.get('support', 0):.2f}, "
                        f"Resistance: ${sr_levels.get('resistance', 0):.2f}")
        
        # Fundamental notes
        pe_ratio = info.get('trailingPE')
        if pe_ratio:
            notes.append(f"P/E Ratio: {pe_ratio:.1f}")
        
        return notes
    
    def screen_all_stocks(self) -> List[ScreenResult]:
        """Screen all stocks in universe"""
        results = []
        
        print(f"🔍 Screening {len(self.stock_universe)} stocks...")
        
        for symbol in self.stock_universe:
            result = self.screen_stock(symbol)
            if result:
                results.append(result)
        
        # Sort by overall score (highest first)
        results.sort(key=lambda x: x.overall_score, reverse=True)
        
        return results
    
    def save_screen_results(self, results: List[ScreenResult], output_dir: str = "technical-screening"):
        """Save screening results to JSON file"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{output_dir}/screen_results_{timestamp}.json"
        
        # Convert to dict for JSON serialization
        results_data = []
        for result in results:
            result_dict = asdict(result)
            # Convert signals to dict as well
            result_dict['signals'] = [asdict(signal) for signal in result.signals]
            results_data.append(result_dict)
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'total_screened': len(results_data),
            'results': results_data,
            'summary': self._generate_screen_summary(results)
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"Screen results saved to: {filename}")
        return filename
    
    def _generate_screen_summary(self, results: List[ScreenResult]) -> Dict:
        """Generate summary statistics from screening results"""
        if not results:
            return {}
        
        recommendations = {}
        for result in results:
            rec = result.recommendation
            recommendations[rec] = recommendations.get(rec, 0) + 1
        
        sectors = {}
        for result in results:
            sector = result.sector
            sectors[sector] = sectors.get(sector, 0) + 1
        
        return {
            'total_stocks': len(results),
            'recommendations': recommendations,
            'sectors': sectors,
            'avg_score': np.mean([r.overall_score for r in results]),
            'top_picks': [r.symbol for r in results[:10]]
        }

def main():
    """Main execution function"""
    print("🎯 Starting Technical Screening System...")
    
    screener = TechnicalScreener()
    
    # Run screening
    results = screener.screen_all_stocks()
    
    # Save results
    output_file = screener.save_screen_results(results)
    
    # Print summary
    print(f"\n✅ Screening Complete!")
    print(f"📊 Total stocks analyzed: {len(results)}")
    print(f"💾 Results saved to: {output_file}")
    
    # Show top picks
    print(f"\n🏆 Top 10 Stock Picks:")
    for i, result in enumerate(results[:10], 1):
        print(f"{i:2d}. {result.symbol:5s} | Score: {result.overall_score:5.1f} | "
              f"Rec: {result.recommendation:10s} | R:R: {result.risk_reward_ratio:.1f}:1")
    
    # Show recommendations breakdown
    recommendations = {}
    for result in results:
        rec = result.recommendation
        recommendations[rec] = recommendations.get(rec, 0) + 1
    
    print(f"\n📈 Recommendations Breakdown:")
    for rec, count in recommendations.items():
        print(f"  {rec}: {count}")

if __name__ == "__main__":
    main()