"""
Model module for the NAV predictor.
Provides functionality to analyze stocks and mutual funds and make buy/sell recommendations.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from matplotlib.ticker import MaxNLocator

# Import utility functions and preprocessing tools
from .utils import (
    fetch_stock_data, search_stock, analyze_stock_trend,
    fetch_mutual_fund_data, search_mutual_fund, analyze_mutual_fund,
    get_similar_stock_recommendations
)
from .preprocess import (
    clean_stock_data, clean_mutual_fund_data, 
    calculate_returns, calculate_technical_indicators,
    prepare_prediction_data
)

# Setup logging
logger = logging.getLogger(__name__)

# Create charts directory if it doesn't exist
os.makedirs("assets/charts", exist_ok=True)

def generate_stock_chart(symbol, stock_data, analysis, exchange="NSE"):
    """
    Generate a chart for stock price and indicators
    
    Args:
        symbol (str): Stock symbol
        stock_data (dict): Stock data
        analysis (dict): Analysis results
        exchange (str): Stock exchange (NSE or BSE)
        
    Returns:
        str: Path to the generated chart image or None if error
    """
    try:
        # Clean and prepare the data
        df = clean_stock_data(stock_data)
        
        if df is None or df.empty:
            logger.error("Cannot generate chart: No data available")
            return None
            
        # Calculate indicators
        df = calculate_technical_indicators(df)
        
        # Set up the figure with subplots - reduce size for web display
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 7), gridspec_kw={'height_ratios': [3, 1, 1]})
        fig.suptitle(f"{symbol} ({exchange}) - Price and Technical Indicators", fontsize=14)
        
        # Plot 1: Price with SMAs
        ax1.plot(df.index, df['close'], label='Close Price', linewidth=2, color='blue')
        ax1.plot(df.index, df['SMA_5'], label='SMA 5', linewidth=1.5, color='red')
        ax1.plot(df.index, df['SMA_20'], label='SMA 20', linewidth=1.5, color='green')
        ax1.plot(df.index, df['SMA_50'], label='SMA 50', linewidth=1.5, color='purple')
        
        # Add Bollinger Bands
        if 'BB_upper' in df.columns and 'BB_lower' in df.columns:
            ax1.fill_between(df.index, df['BB_upper'], df['BB_lower'], alpha=0.2, color='gray', label='Bollinger Bands')
        
        ax1.set_title('Price and Moving Averages', fontsize=12)
        ax1.set_ylabel('Price (₹)', fontsize=10)
        ax1.legend(loc='upper left', fontsize=9)
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: RSI
        if 'RSI_14' in df.columns:
            ax2.plot(df.index, df['RSI_14'], label='RSI (14)', color='orange', linewidth=1.5)
            ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5)
            ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5)
            ax2.set_title('Relative Strength Index (RSI)', fontsize=12)
            ax2.set_ylabel('RSI', fontsize=10)
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
        
        # Plot 3: MACD
        if 'MACD' in df.columns and 'MACD_signal' in df.columns:
            ax3.plot(df.index, df['MACD'], label='MACD', color='blue', linewidth=1.5)
            ax3.plot(df.index, df['MACD_signal'], label='Signal Line', color='red', linewidth=1.5)
            
            # Color MACD histogram
            if 'MACD_histogram' in df.columns:
                for i in range(len(df.index)):
                    if i > 0:  # Skip first point
                        # Use green for positive, red for negative
                        color = 'green' if df['MACD_histogram'].iloc[i] > 0 else 'red'
                        ax3.bar(df.index[i], df['MACD_histogram'].iloc[i], color=color, width=1)
            
            ax3.set_title('Moving Average Convergence Divergence (MACD)', fontsize=12)
            ax3.set_ylabel('MACD', fontsize=10)
            ax3.grid(True, alpha=0.3)
            ax3.legend(loc='upper left', fontsize=9)
        
        # Add recommendation and current price
        latest_price = analysis.get("latest_price", "N/A")
        recommendation = analysis.get("final_recommendation", analysis.get("recommendation", "N/A"))
        trend = analysis.get("trend", "N/A")
        
        # Add text annotation for price and recommendation
        annotation_text = f"Current Price: ₹{latest_price} | Trend: {trend} | Recommendation: {recommendation}"
        fig.text(0.5, 0.01, annotation_text, ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        # Format x-axis dates - keep fewer ticks for cleaner look
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, fontsize=8)
            # Reduce number of x-ticks - Use MaxNLocator from ticker module not dates
            ax.xaxis.set_major_locator(MaxNLocator(6))
        
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.05)
        
        # Create charts directory if it doesn't exist (do this again to be sure)
        charts_dir = os.path.abspath("assets/charts")
        os.makedirs(charts_dir, exist_ok=True)
        
        # Save chart with reduced size and higher quality
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{symbol}_{exchange}_{timestamp}.png"
        chart_path = os.path.join(charts_dir, filename)
        
        # Save the chart
        plt.savefig(chart_path, dpi=90, bbox_inches='tight', pad_inches=0.2)
        plt.close(fig)
        
        # Convert to relative path for serving
        rel_chart_path = os.path.join("assets/charts", filename)
        
        # Log success
        logger.info(f"Generated stock chart: {rel_chart_path}")
        logger.info(f"Chart saved to: {chart_path}")
        
        # Check if file was created
        if not os.path.exists(chart_path):
            logger.error(f"Failed to create chart file at: {chart_path}")
            return None
            
        return rel_chart_path
    except Exception as e:
        logger.error(f"Error generating stock chart: {str(e)}")
        return None

def generate_mutual_fund_chart(fund_code, fund_data, analysis):
    """
    Generate a chart for mutual fund NAV and indicators
    
    Args:
        fund_code (str): Mutual fund code
        fund_data (dict): Fund data
        analysis (dict): Analysis results
        
    Returns:
        str: Path to the generated chart image or None if error
    """
    try:
        # Clean and prepare the data
        df = clean_mutual_fund_data(fund_data)
        
        if df is None or df.empty:
            logger.error("Cannot generate chart: No data available")
            return None
            
        # Calculate indicators
        df = calculate_returns(df)
        df = calculate_technical_indicators(df)
        
        # Set up the figure with subplots - reduce size for web display
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 7), gridspec_kw={'height_ratios': [3, 1, 1]})
        
        scheme_name = analysis.get("scheme_name", fund_data.get("meta", {}).get("scheme_name", "Unknown Fund"))
        # Truncate long scheme names
        if len(scheme_name) > 50:
            scheme_name = scheme_name[:47] + "..."
        fig.suptitle(f"{scheme_name} - NAV and Performance", fontsize=14)
        
        # Plot 1: NAV with SMAs
        ax1.plot(df.index, df['nav'], label='NAV', linewidth=2, color='blue')
        ax1.plot(df.index, df['SMA_5'], label='SMA 5', linewidth=1.5, color='red')
        ax1.plot(df.index, df['SMA_20'], label='SMA 20', linewidth=1.5, color='green')
        ax1.plot(df.index, df['SMA_50'], label='SMA 50', linewidth=1.5, color='purple')
        
        # Add Bollinger Bands
        if 'BB_upper' in df.columns and 'BB_lower' in df.columns:
            ax1.fill_between(df.index, df['BB_upper'], df['BB_lower'], alpha=0.2, color='gray', label='Bollinger Bands')
        
        ax1.set_title('NAV and Moving Averages', fontsize=12)
        ax1.set_ylabel('NAV (₹)', fontsize=10)
        ax1.legend(loc='upper left', fontsize=9)
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Daily Returns
        daily_returns = df['nav'].pct_change() * 100
        ax2.plot(df.index, daily_returns, label='Daily Returns (%)', color='green', linewidth=1)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_title('Daily Returns (%)', fontsize=12)
        ax2.set_ylabel('Return (%)', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Cumulative Returns
        if 'return_30d' in df.columns:
            ax3.plot(df.index, df['return_30d'], label='30-Day Return (%)', color='blue', linewidth=1.5)
        
        # Add 7-day returns if available
        if 'return_7d' in df.columns:
            ax3.plot(df.index, df['return_7d'], label='7-Day Return (%)', color='orange', linewidth=1.5)
        
        ax3.set_title('Rolling Returns (%)', fontsize=12)
        ax3.set_ylabel('Return (%)', fontsize=10)
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax3.grid(True, alpha=0.3)
        ax3.legend(loc='upper left', fontsize=9)
        
        # Add recommendation and current NAV
        latest_nav = analysis.get("latest_nav", "N/A")
        recommendation = analysis.get("recommendation", "N/A")
        sip_recommendation = analysis.get("sip_recommendation", "N/A")
        trend = analysis.get("trend", "N/A")
        
        # Add text annotation for NAV and recommendation - simplify for smaller chart
        annotation_text = f"Current NAV: ₹{latest_nav} | Trend: {trend}"
        fig.text(0.5, 0.01, annotation_text, ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        # Format x-axis dates - keep fewer ticks for cleaner look
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, fontsize=8)
            # Reduce number of x-ticks - Use MaxNLocator from ticker module not dates
            ax.xaxis.set_major_locator(MaxNLocator(6))
        
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.05)
        
        # Create charts directory if it doesn't exist (do this again to be sure)
        charts_dir = os.path.abspath("assets/charts")
        os.makedirs(charts_dir, exist_ok=True)
        
        # Save chart with reduced size and higher quality
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"fund_{fund_code}_{timestamp}.png"
        chart_path = os.path.join(charts_dir, filename)
        
        # Save the chart
        plt.savefig(chart_path, dpi=90, bbox_inches='tight', pad_inches=0.2)
        plt.close(fig)
        
        # Convert to relative path for serving
        rel_chart_path = os.path.join("assets/charts", filename)
        
        # Log success
        logger.info(f"Generated mutual fund chart: {rel_chart_path}")
        logger.info(f"Chart saved to: {chart_path}")
        
        # Check if file was created
        if not os.path.exists(chart_path):
            logger.error(f"Failed to create chart file at: {chart_path}")
            return None
            
        return rel_chart_path
    except Exception as e:
        logger.error(f"Error generating mutual fund chart: {str(e)}")
        return None

class StockAnalyzer:
    """Class for analyzing stocks and providing recommendations"""
    
    def __init__(self):
        """Initialize the StockAnalyzer"""
        pass
        
    def search(self, query, exchange="NSE"):
        """
        Search for a stock by name or symbol
        
        Args:
            query (str): The search query
            exchange (str): Stock exchange (NSE or BSE)
            
        Returns:
            list: List of matching stocks
        """
        return search_stock(query, exchange)
        
    def analyze(self, symbol, exchange="NSE", days=30):
        """
        Analyze a stock and provide recommendations
        
        Args:
            symbol (str): Stock symbol
            exchange (str): Stock exchange (NSE or BSE)
            days (int): Number of days to analyze
            
        Returns:
            dict: Analysis results with recommendation
        """
        try:
            # Fetch stock data
            stock_data = fetch_stock_data(symbol, exchange)
            
            if "error" in stock_data:
                return stock_data
                
            # Analyze trend
            analysis = analyze_stock_trend(stock_data, days)
            
            # Get more detailed technical analysis
            df = clean_stock_data(stock_data)
            
            if df is not None and not df.empty:
                df = calculate_returns(df)
                df = calculate_technical_indicators(df)
                df = prepare_prediction_data(df)
                
                # Get the latest data point
                latest = df.iloc[-1]
                
                # Additional signals
                # 1. RSI Signal
                rsi = latest.get('RSI_14')
                rsi_signal = ""
                if rsi is not None:
                    if rsi > 70:
                        rsi_signal = "Overbought - potential sell signal"
                    elif rsi < 30:
                        rsi_signal = "Oversold - potential buy signal"
                    else:
                        rsi_signal = "Neutral"
                
                # 2. MACD Signal
                macd = latest.get('MACD')
                macd_signal_line = latest.get('MACD_signal')
                macd_cross_signal = ""
                if macd is not None and macd_signal_line is not None:
                    if macd > macd_signal_line:
                        macd_cross_signal = "Bullish - MACD above signal line"
                    else:
                        macd_cross_signal = "Bearish - MACD below signal line"
                
                # 3. Bollinger Bands Signal
                bb_upper = latest.get('BB_upper')
                bb_lower = latest.get('BB_lower')
                close = latest.get('close')
                bb_signal = ""
                if bb_upper is not None and bb_lower is not None and close is not None:
                    if close > bb_upper:
                        bb_signal = "Price above upper Bollinger Band - potential sell signal"
                    elif close < bb_lower:
                        bb_signal = "Price below lower Bollinger Band - potential buy signal"
                    else:
                        bb_signal = "Price within Bollinger Bands - neutral"
                
                # 4. Moving Average Signals
                sma_5 = latest.get('SMA_5')
                sma_20 = latest.get('SMA_20')
                sma_50 = latest.get('SMA_50')
                ma_signals = []
                
                if sma_5 is not None and sma_20 is not None:
                    if sma_5 > sma_20:
                        ma_signals.append("Short-term uptrend (SMA5 > SMA20)")
                    else:
                        ma_signals.append("Short-term downtrend (SMA5 < SMA20)")
                
                if sma_20 is not None and sma_50 is not None:
                    if sma_20 > sma_50:
                        ma_signals.append("Medium-term uptrend (SMA20 > SMA50)")
                    else:
                        ma_signals.append("Medium-term downtrend (SMA20 < SMA50)")
                
                # Add technical indicators to analysis
                analysis["technical_indicators"] = {
                    "rsi_14": round(rsi, 2) if rsi is not None else None,
                    "rsi_signal": rsi_signal,
                    "macd_signal": macd_cross_signal,
                    "bollinger_band_signal": bb_signal,
                    "moving_average_signals": ma_signals
                }
                
                # Refine recommendation based on technical indicators
                buy_signals = 0
                sell_signals = 0
                
                # Count buy signals
                if rsi is not None and rsi < 30:
                    buy_signals += 1
                if macd is not None and macd_signal_line is not None and macd > macd_signal_line:
                    buy_signals += 1
                if close is not None and bb_lower is not None and close < bb_lower:
                    buy_signals += 1
                if sma_5 is not None and sma_20 is not None and sma_5 > sma_20:
                    buy_signals += 1
                if sma_20 is not None and sma_50 is not None and sma_20 > sma_50:
                    buy_signals += 1
                
                # Count sell signals
                if rsi is not None and rsi > 70:
                    sell_signals += 1
                if macd is not None and macd_signal_line is not None and macd < macd_signal_line:
                    sell_signals += 1
                if close is not None and bb_upper is not None and close > bb_upper:
                    sell_signals += 1
                if sma_5 is not None and sma_20 is not None and sma_5 < sma_20:
                    sell_signals += 1
                if sma_20 is not None and sma_50 is not None and sma_20 < sma_50:
                    sell_signals += 1
                
                # Final recommendation score
                score = buy_signals - sell_signals
                
                if score >= 3:
                    final_recommendation = "Strong Buy"
                elif score == 2:
                    final_recommendation = "Buy"
                elif score == 1:
                    final_recommendation = "Weak Buy"
                elif score == 0:
                    final_recommendation = "Hold"
                elif score == -1:
                    final_recommendation = "Weak Sell"
                elif score == -2:
                    final_recommendation = "Sell"
                else:  # score <= -3
                    final_recommendation = "Strong Sell"
                
                analysis["final_recommendation"] = final_recommendation
                analysis["buy_signals"] = buy_signals
                analysis["sell_signals"] = sell_signals
                
                # Add future price estimate (very simplified)
                latest_price = analysis.get("latest_price", 0)
                daily_change = analysis.get("daily_change_percentage", 0)
                period_change = analysis.get("period_change_percentage", 0)
                
                # Estimate future price based on recent trend (very simplified)
                tomorrow_est = latest_price * (1 + (daily_change / 100))
                week_est = latest_price * (1 + (period_change / 100) * (7 / days))
                month_est = latest_price * (1 + (period_change / 100) * (30 / days))
                
                analysis["price_estimates"] = {
                    "tomorrow": round(tomorrow_est, 2),
                    "1_week": round(week_est, 2),
                    "1_month": round(month_est, 2),
                    "note": "These estimates are based on simple trend extrapolation and should not be the sole basis for investment decisions."
                }
                
                # Get similar stock recommendations
                similar_stocks = get_similar_stock_recommendations(symbol, exchange, 5, include_both_exchanges=True)
                analysis["similar_stock_recommendations"] = similar_stocks
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing stock: {str(e)}")
            return {"error": f"Error analyzing stock: {str(e)}"}
    
    def get_stock_info(self, query, exchange="NSE"):
        """
        Search for a stock and provide full information
        
        Args:
            query (str): Stock name or symbol
            exchange (str): Stock exchange (NSE or BSE) for preferential matching,
                            but will auto-detect the actual exchange
            
        Returns:
            dict: Stock information and analysis
        """
        try:
            # First search for the stock
            search_results = self.search(query, exchange)
            
            if not search_results:
                # If no results in the preferred exchange, try the other exchange
                other_exchange = "BSE" if exchange.upper() == "NSE" else "NSE"
                search_results = self.search(query, other_exchange)
                if not search_results:
                    return {"error": f"No stocks found matching '{query}' on NSE or BSE"}
            
            # Use the first match
            stock = search_results[0]
            symbol = stock.get("symbol", "").split(".")[0]  # Remove exchange suffix
            
            # Auto-detect which exchange the stock belongs to
            detected_exchange = stock.get("detected_exchange", exchange)
            
            # Log the auto-detection
            logger.info(f"Auto-detected exchange for {symbol}: {detected_exchange}")
            
            # Get full analysis using the detected exchange
            analysis = self.analyze(symbol, detected_exchange)
            
            # Ensure we have similar stock recommendations from both exchanges
            if "similar_stock_recommendations" not in analysis:
                similar_stocks = get_similar_stock_recommendations(symbol, detected_exchange, 5, include_both_exchanges=True)
                analysis["similar_stock_recommendations"] = similar_stocks
            
            # Add stock info to analysis
            analysis["stock_info"] = {
                "name": stock.get("shortname", stock.get("longname", "Unknown")),
                "symbol": symbol,
                "exchange": detected_exchange,
                "type": stock.get("typeDisp", "Stock"),
                "sector": stock.get("sector", "Unknown"),
                "industry": stock.get("industry", "Unknown")
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error getting stock info: {str(e)}")
            return {"error": f"Error getting stock info: {str(e)}"}


class MutualFundAnalyzer:
    """Class for analyzing mutual funds and providing recommendations"""
    
    def __init__(self):
        """Initialize the MutualFundAnalyzer"""
        pass
        
    def search(self, query):
        """
        Search for a mutual fund by name
        
        Args:
            query (str): The search query
            
        Returns:
            list: List of matching mutual funds
        """
        return search_mutual_fund(query)
        
    def analyze(self, fund_code, days=30):
        """
        Analyze a mutual fund and provide recommendations
        
        Args:
            fund_code (str): Mutual fund code
            days (int): Number of days to analyze
            
        Returns:
            dict: Analysis results with recommendation
        """
        try:
            # Fetch mutual fund data
            fund_data = fetch_mutual_fund_data(fund_code)
            
            if "error" in fund_data:
                return fund_data
                
            # Analyze trend
            analysis = analyze_mutual_fund(fund_data, days)
            
            # Get more detailed technical analysis
            df = clean_mutual_fund_data(fund_data)
            
            if df is not None and not df.empty:
                df = calculate_returns(df)
                df = calculate_technical_indicators(df)
                df = prepare_prediction_data(df)
                
                # Get the latest data point
                latest = df.iloc[-1]
                
                # Calculate additional metrics for mutual funds
                
                # 1. Consistency Score
                # Check if returns are consistently positive
                returns_30d = df['return_30d'].dropna()
                positive_days = (returns_30d > 0).sum()
                total_days = len(returns_30d)
                consistency_score = (positive_days / total_days) * 10 if total_days > 0 else 0
                
                # 2. Volatility (standard deviation of daily returns)
                daily_returns = df['nav'].pct_change().dropna()
                volatility = daily_returns.std() * 100
                
                # 3. Risk-adjusted return (Sharpe ratio approximation)
                # Assuming risk-free rate of 4% annually (0.011% daily)
                risk_free_rate = 0.04 / 365
                excess_return = daily_returns - risk_free_rate
                sharpe_ratio = (excess_return.mean() / daily_returns.std()) * np.sqrt(252) if daily_returns.std() > 0 else 0
                
                # Add metrics to analysis
                analysis["additional_metrics"] = {
                    "consistency_score": round(consistency_score, 2),
                    "volatility_percentage": round(volatility, 2),
                    "sharpe_ratio": round(sharpe_ratio, 2)
                }
                
                # SIP recommendation
                # If fund is performing well and has good consistency, recommend SIP
                if analysis.get("trend") in ["Strong Upward", "Upward"] and consistency_score > 6:
                    sip_recommendation = "Recommended for SIP investments"
                elif analysis.get("trend") == "Sideways" and consistency_score > 5:
                    sip_recommendation = "Suitable for SIP investments with regular monitoring"
                elif analysis.get("trend") in ["Downward", "Strong Downward"] and consistency_score > 7:
                    sip_recommendation = "Consider SIP for cost averaging, but review fund fundamentals"
                else:
                    sip_recommendation = "Research further before starting SIP investments"
                
                analysis["sip_recommendation"] = sip_recommendation
                
                # Add NAV estimate (very simplified)
                latest_nav = analysis.get("latest_nav", 0)
                daily_change = analysis.get("daily_change_percentage", 0)
                period_change = analysis.get("period_change_percentage", 0)
                
                # Estimate future NAV based on recent trend (very simplified)
                tomorrow_est = latest_nav * (1 + (daily_change / 100))
                week_est = latest_nav * (1 + (period_change / 100) * (7 / days))
                month_est = latest_nav * (1 + (period_change / 100) * (30 / days))
                
                analysis["nav_estimates"] = {
                    "tomorrow": round(tomorrow_est, 2),
                    "1_week": round(week_est, 2),
                    "1_month": round(month_est, 2),
                    "note": "These estimates are based on simple trend extrapolation and should not be the sole basis for investment decisions."
                }
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing mutual fund: {str(e)}")
            return {"error": f"Error analyzing mutual fund: {str(e)}"}
    
    def get_fund_info(self, query):
        """
        Search for a mutual fund and provide full information
        
        Args:
            query (str): Mutual fund name
            
        Returns:
            dict: Mutual fund information and analysis
        """
        try:
            # First search for the fund
            search_results = self.search(query)
            
            if not search_results:
                return {"error": f"No mutual funds found matching '{query}'"}
            
            # Use the first match
            fund = search_results[0]
            fund_code = fund.get("schemeCode", "")
            
            # Get full analysis
            analysis = self.analyze(fund_code)
            
            # Add fund info to analysis
            analysis["fund_info"] = {
                "name": fund.get("schemeName", "Unknown Fund"),
                "fund_code": fund_code
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error getting mutual fund info: {str(e)}")
            return {"error": f"Error getting mutual fund info: {str(e)}"}


def format_stock_analysis_response(analysis, include_chart=True):
    """
    Format the stock analysis results into a readable response
    
    Args:
        analysis (dict): Stock analysis results
        include_chart (bool): Whether to include chart path in response
        
    Returns:
        str: Formatted response
    """
    if "error" in analysis:
        return f"Error: {analysis['error']}"
        
    symbol = analysis.get("symbol", "Unknown")
    company_name = analysis.get("company_name", "Unknown Company")
    
    # Get stock info if available
    stock_info = analysis.get("stock_info", {})
    if stock_info:
        company_name = stock_info.get("name", company_name)
        symbol = stock_info.get("symbol", symbol)
    
    exchange = analysis.get("exchange", stock_info.get("exchange", "NSE"))
    sector = stock_info.get("sector", "Unknown")
    industry = stock_info.get("industry", "Unknown")
    latest_price = analysis.get("latest_price", "N/A")
    daily_change = analysis.get("daily_change_percentage", "N/A")
    period_change = analysis.get("period_change_percentage", "N/A")
    period_days = analysis.get("period_days", 30)
    trend = analysis.get("trend", "Neutral")
    recommendation = analysis.get("final_recommendation", analysis.get("recommendation", "Hold"))
    
    # Format stock indicators
    indicators = analysis.get("technical_indicators", {})
    
    rsi = indicators.get("rsi_14", "N/A")
    rsi_signal = indicators.get("rsi_signal", "")
    macd_signal = indicators.get("macd_signal", "")
    bb_signal = indicators.get("bollinger_band_signal", "")
    ma_signals = indicators.get("moving_average_signals", [])
    
    # Format price estimates
    estimates = analysis.get("price_estimates", {})
    tomorrow_est = estimates.get("tomorrow", "N/A")
    week_est = estimates.get("1_week", "N/A")
    month_est = estimates.get("1_month", "N/A")
    
    # Get buy/sell signals count if available
    buy_signals = analysis.get("buy_signals")
    sell_signals = analysis.get("sell_signals")
    
    # Create a more enthusiastic direct recommendation at the beginning
    direct_recommendation = ""
    buy_recommendation_reason = ""
    
    if recommendation in ["Strong Buy", "Buy"]:
        direct_recommendation = f"✅ YES! {company_name} looks like an excellent buying opportunity at ₹{latest_price}!"
        buy_recommendation_reason = f"\n\n💡 Why you should buy: The stock shows strong technical signals with {buy_signals} buy indicators and only {sell_signals} sell indicators. The stock is in a {trend.lower()} trend, and technical analysis suggests potential for upward movement." 
        if ma_signals and any("uptrend" in signal.lower() for signal in ma_signals):
            buy_recommendation_reason += " Moving averages indicate an uptrend which is a bullish sign."
        if macd_signal and "bullish" in macd_signal.lower():
            buy_recommendation_reason += " MACD signals bullish momentum."
        if period_change and isinstance(period_change, (int, float)) and period_change > 0:
            buy_recommendation_reason += f" The stock has shown positive momentum with a {period_change:.2f}% change over the last {period_days} days."
        
    elif recommendation == "Weak Buy":
        direct_recommendation = f"✅ Yes, you can consider buying {company_name} at ₹{latest_price}, though there are some mixed signals."
        buy_recommendation_reason = f"\n\n💡 Why you might consider buying: The stock shows more positive signals ({buy_signals}) than negative ones ({sell_signals}), though the difference is not substantial. The stock is in a {trend.lower()} trend, but there are some mixed indicators."
        if ma_signals:
            for signal in ma_signals:
                if "uptrend" in signal.lower():
                    buy_recommendation_reason += f" {signal}, which is positive."
                elif "downtrend" in signal.lower():
                    buy_recommendation_reason += f" However, {signal}, which suggests caution."
        
    elif recommendation == "Hold":
        direct_recommendation = f"⚠️ {company_name} is currently rated as HOLD at ₹{latest_price}. If you already own it, keep it, but there may be better buying opportunities."
        buy_recommendation_reason = f"\n\n💡 Why it's rated as HOLD: The technical indicators are balanced with {buy_signals} buy signals and {sell_signals} sell signals. The stock is showing a {trend.lower()} trend. Consider waiting for a clearer entry point."
        
    elif recommendation == "Weak Sell":
        direct_recommendation = f"❌ Not recommended to buy {company_name} at this time. The analysis suggests it might be slightly overvalued at ₹{latest_price}."
        buy_recommendation_reason = f"\n\n❌ Why you should avoid buying now: The stock shows more negative signals ({sell_signals}) than positive ones ({buy_signals}). The {trend.lower()} trend doesn't support a buy recommendation at current levels."
        if ma_signals and any("downtrend" in signal.lower() for signal in ma_signals):
            buy_recommendation_reason += " Moving averages indicate a downtrend which is concerning for short-term performance."
        
    elif recommendation in ["Sell", "Strong Sell"]:
        direct_recommendation = f"❌ NO! This is not a good time to buy {company_name}. The analysis strongly suggests avoiding this stock at the current price of ₹{latest_price}."
        buy_recommendation_reason = f"\n\n❌ Why you should NOT buy: The technical analysis shows strong negative signals with {sell_signals} sell indicators compared to only {buy_signals} buy indicators. The stock is in a {trend.lower()} trend, suggesting potential further decline."
        if ma_signals and any("downtrend" in signal.lower() for signal in ma_signals):
            buy_recommendation_reason += " Moving averages confirm a downtrend which is a bearish sign."
        if macd_signal and "bearish" in macd_signal.lower():
            buy_recommendation_reason += " MACD signals bearish momentum."
    
    # Formatted stock header
    response = [
        direct_recommendation,
        f"\n📊 Stock: {company_name} ({symbol})",
        f"Exchange: {exchange}",
        f"Sector: {sector}",
        f"Industry: {industry}",
        f"Current Price: ₹{latest_price}",
        f"Daily Change: {daily_change:.2f}%" if isinstance(daily_change, (int, float)) else f"Daily Change: {daily_change}",
        f"Monthly Change: {period_change:.2f}%" if isinstance(period_change, (int, float)) else f"{period_days}-Day Change: {period_change}"
    ]
    
    # Add technical indicators in a structured format
    if indicators:
        response.append("\n📈 Technical Indicators:")
        if isinstance(rsi, (int, float)):
            # Add interpretation of RSI
            rsi_interpretation = ""
            if rsi > 70:
                rsi_interpretation = "Overbought"
            elif rsi < 30:
                rsi_interpretation = "Oversold"
            else:
                rsi_interpretation = "Neutral"
            response.append(f"RSI (14): {rsi:.2f} - {rsi_interpretation}")
        else:
            response.append(f"RSI (14): {rsi} - {rsi_signal}")
            
        response.append(f"MACD: {macd_signal}")
        response.append(f"Bollinger Bands: {bb_signal}")
        
        if ma_signals:
            response.append("Moving Averages:")
            for signal in ma_signals:
                response.append(f"  - {signal}")
                
        # Add overall trend
        response.append(f"Trend: {trend}")
        
        # Add moving average signal interpretation
        if ma_signals:
            if any("uptrend" in signal.lower() for signal in ma_signals) and any("downtrend" in signal.lower() for signal in ma_signals):
                if "uptrend" in ma_signals[0].lower():
                    response.append("Moving Average Signal: Potential reversal to downside")
                else:
                    response.append("Moving Average Signal: Potential reversal to upside")
            elif all("uptrend" in signal.lower() for signal in ma_signals):
                response.append("Moving Average Signal: Strong uptrend")
            elif all("downtrend" in signal.lower() for signal in ma_signals):
                response.append("Moving Average Signal: Strong downtrend")
    
    # Add price estimates if available
    if estimates:
        response.append("\n💰 Price Estimates:")
        response.append(f"Tomorrow: ₹{tomorrow_est}")
        response.append(f"1 Week: ₹{week_est}")
        response.append(f"1 Month: ₹{month_est}")
    
    # Add analysis summary
    response.append("\n🔍 Analysis Summary:")
    response.append(f"Buy Signals: {buy_signals}")
    response.append(f"Sell Signals: {sell_signals}")
    response.append(f"Final Recommendation: {recommendation}")
    
    # Add the buying recommendation reason
    response.append(buy_recommendation_reason)
    
    # Add disclaimer
    response.append("\n⚠️ Disclaimer: This analysis is based on historical data and technical indicators. Market conditions can change rapidly, and this should not be considered as financial advice. Always do your own research before making investment decisions.")
    
    # Add chart path if available and requested
    chart_path = analysis.get("chart_path")
    if include_chart and chart_path:
        response.append(f"\n📊 Chart available at: {chart_path}")
    
    # Add similar stock recommendations if available, organized by exchange with stronger wording
    similar_stocks = analysis.get("similar_stock_recommendations", [])
    if similar_stocks:
        # Separate recommendations by exchange
        nse_stocks = [s for s in similar_stocks if s.get("exchange", "").upper() == "NSE" or ".NS" in s.get("symbol", "")]
        bse_stocks = [s for s in similar_stocks if s.get("exchange", "").upper() == "BSE" or ".BO" in s.get("symbol", "")]
        
        response.append("\n🔍 You should also check out these alternative stocks:")
        
        # Add NSE stocks
        if nse_stocks:
            response.append("\n  📈 NSE Stocks You Might Like:")
            for i, stock in enumerate(nse_stocks, 1):
                symbol = stock.get("symbol", "").replace(".NS", "")
                name = stock.get("name", "Unknown")
                response.append(f"  {i}. {name} ({symbol})")
        
        # Add BSE stocks
        if bse_stocks:
            response.append("\n  📈 BSE Stocks Worth Considering:")
            for i, stock in enumerate(bse_stocks, 1):
                symbol = stock.get("symbol", "").replace(".BO", "")
                name = stock.get("name", "Unknown")
                response.append(f"  {i}. {name} ({symbol})")
    
    return "\n".join(response)


def format_mutual_fund_analysis_response(analysis, include_chart=True):
    """
    Format mutual fund analysis results into a human-readable response with point-by-point format
    
    Args:
        analysis (dict): Mutual fund analysis results
        include_chart (bool): Whether to include a chart
        
    Returns:
        str: Formatted response
    """
    try:
        if "error" in analysis:
            return f"Sorry, I couldn't analyze the mutual fund: {analysis['error']}"
            
        response = []
        chart_path = None
        
        # Generate chart if requested
        if include_chart and "fund_info" in analysis:
            fund_info = analysis["fund_info"]
            fund_code = fund_info.get("fund_code")
            
            # Get the original fund data
            fund_data = fetch_mutual_fund_data(fund_code)
            if "error" not in fund_data:
                chart_path = generate_mutual_fund_chart(fund_code, fund_data, analysis)
        
        # Add chart reference if generated - Make this more prominent for easy detection by server
        if chart_path:
            # This format is specifically designed to be easily detected by the server
            response.append(f"📊 MUTUAL FUND CHART: {chart_path}")
            response.append("")
        
        # 1. BASIC INFORMATION
        response.append("1️⃣ BASIC INFORMATION:")
        
        # Add fund info if available
        if "fund_info" in analysis:
            fund_info = analysis["fund_info"]
            response.append(f"• Mutual Fund: {fund_info.get('name')}")
            response.append(f"• Fund Code: {fund_info.get('fund_code')}")
        
        # Add scheme info
        response.append(f"• Fund House: {analysis.get('fund_house', 'N/A')}")
        response.append(f"• Scheme Type: {analysis.get('scheme_type', 'N/A')}")
        
        # 2. CURRENT NAV INFORMATION
        response.append("")
        response.append("2️⃣ CURRENT NAV INFORMATION:")
        response.append(f"• Current NAV: ₹{analysis.get('latest_nav', 'N/A')}")
        response.append(f"• Daily Change: {analysis.get('daily_change_percentage', 'N/A')}%")
        response.append(f"• Monthly Change: {analysis.get('period_change_percentage', 'N/A')}%")
        response.append(f"• Estimated Annual Return: {analysis.get('estimated_annual_return', 'N/A')}%")
        
        # 3. PERFORMANCE METRICS
        response.append("")
        response.append("3️⃣ PERFORMANCE METRICS:")
        
        if "additional_metrics" in analysis:
            metrics = analysis["additional_metrics"]
            response.append(f"• Consistency Score (0-10): {metrics.get('consistency_score', 'N/A')}")
            response.append(f"• Volatility: {metrics.get('volatility_percentage', 'N/A')}%")
            response.append(f"• Sharpe Ratio: {metrics.get('sharpe_ratio', 'N/A')}")
        
        # 4. TREND ANALYSIS
        response.append("")
        response.append("4️⃣ TREND ANALYSIS:")
        response.append(f"• Trend: {analysis.get('trend', 'N/A')}")
        
        # 5. NAV ESTIMATES
        response.append("")
        response.append("5️⃣ NAV ESTIMATES:")
        
        if "nav_estimates" in analysis:
            estimates = analysis["nav_estimates"]
            response.append(f"• Tomorrow: ₹{estimates.get('tomorrow', 'N/A')}")
            response.append(f"• 1 Week: ₹{estimates.get('1_week', 'N/A')}")
            response.append(f"• 1 Month: ₹{estimates.get('1_month', 'N/A')}")
        
        # 6. RECOMMENDATIONS
        response.append("")
        response.append("6️⃣ ANALYSIS SUMMARY & RECOMMENDATIONS:")
        
        # Add SIP recommendation if available
        if "sip_recommendation" in analysis:
            response.append(f"• SIP Recommendation: {analysis.get('sip_recommendation', 'N/A')}")
        
        # Add general recommendation
        response.append(f"• General Recommendation: {analysis.get('recommendation', 'N/A')}")
        
        # 7. DISCLAIMER
        response.append("")
        response.append("7️⃣ DISCLAIMER:")
        response.append("• This analysis is based on historical NAV data.")
        response.append("• Market conditions can change rapidly.")
        response.append("• This should not be considered as financial advice.")
        response.append("• Always do your own research before making investment decisions.")
        
        return "\n".join(response)
    except Exception as e:
        logger.error(f"Error formatting mutual fund analysis: {str(e)}")
        return f"Sorry, I couldn't format the mutual fund analysis: {str(e)}"
