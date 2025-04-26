"""
Utility functions for the NAV predictor module.
Handles data fetching, processing, and analysis tools for stocks and mutual funds.
"""

import requests
import pandas as pd
import numpy as np
import json
import re
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random

# Setup logging
logger = logging.getLogger(__name__)

# API endpoints and URLs
MUTUAL_FUND_API = "https://api.mfapi.in/mf/"  # Free Mutual Fund API
NSE_URL = "https://www.nseindia.com/api/quote-equity?symbol="
BSE_URL = "https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w"
YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"

# Headers to mimic browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def fetch_mutual_fund_data(fund_code):
    """
    Fetch mutual fund NAV data using the MFAPI.
    
    Args:
        fund_code (str): The mutual fund code
        
    Returns:
        dict: Fund data including historical NAVs or error message
    """
    try:
        response = requests.get(f"{MUTUAL_FUND_API}{fund_code}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            logger.error(f"Failed to fetch mutual fund data: {response.status_code}")
            return {"error": f"Failed to fetch mutual fund data: {response.status_code}"}
    except Exception as e:
        logger.error(f"Error fetching mutual fund data: {str(e)}")
        return {"error": f"Error fetching mutual fund data: {str(e)}"}

def search_mutual_fund(query):
    """
    Search for mutual funds matching the given query.
    
    Args:
        query (str): Search query for mutual fund
        
    Returns:
        list: List of matching mutual funds with their codes
    """
    try:
        # The MFAPI doesn't provide a search endpoint, so we'll use a workaround
        # This endpoint returns a JSON file with all mutual funds
        response = requests.get("https://api.mfapi.in/mf", timeout=10)
        if response.status_code == 200:
            all_funds = response.json()
            # Filter funds that match the query
            matching_funds = [fund for fund in all_funds 
                              if query.lower() in fund.get('schemeName', '').lower()]
            
            # Return the top 5 matches
            return matching_funds[:5]
        else:
            logger.error(f"Failed to search mutual funds: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error searching mutual funds: {str(e)}")
        return []

def fetch_stock_data(symbol, exchange="NSE"):
    """
    Fetch stock data from NSE or BSE.
    
    Args:
        symbol (str): Stock symbol
        exchange (str): Stock exchange (NSE or BSE)
        
    Returns:
        dict: Stock data or error message
    """
    try:
        if exchange.upper() == "NSE":
            # Use Yahoo Finance as fallback for NSE data
            stock_symbol = f"{symbol}.NS"
            url = f"{YAHOO_FINANCE_URL}{stock_symbol}"
            params = {
                "range": "1mo",
                "interval": "1d"
            }
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {"status": "success", "data": data}
            else:
                logger.error(f"Failed to fetch NSE stock data: {response.status_code}")
                return {"error": f"Failed to fetch stock data: {response.status_code}"}
                
        elif exchange.upper() == "BSE":
            # Use Yahoo Finance as fallback for BSE data
            stock_symbol = f"{symbol}.BO"
            url = f"{YAHOO_FINANCE_URL}{stock_symbol}"
            params = {
                "range": "1mo",
                "interval": "1d"
            }
            response = requests.get(url, params=params, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {"status": "success", "data": data}
            else:
                logger.error(f"Failed to fetch BSE stock data: {response.status_code}")
                return {"error": f"Failed to fetch stock data: {response.status_code}"}
        else:
            return {"error": "Invalid exchange. Choose either NSE or BSE."}
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        return {"error": f"Error fetching stock data: {str(e)}"}

def search_stock(query, exchange="NSE"):
    """
    Search for stocks matching the given query.
    
    Args:
        query (str): Search query for stock
        exchange (str): Stock exchange (NSE or BSE) for preferential matching
        
    Returns:
        list: List of matching stocks with exchange information
    """
    try:
        # Using Yahoo Finance for search
        url = f"https://query1.finance.yahoo.com/v1/finance/search"
        params = {
            "q": query,
            "quotesCount": 15,  # Increased to get more potential matches
            "newsCount": 0
        }
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            quotes = data.get("quotes", [])
            
            # Get both NSE and BSE stocks
            nse_quotes = [q for q in quotes if q.get("exchange") == "NSI" or ".NS" in q.get("symbol", "")]
            bse_quotes = [q for q in quotes if q.get("exchange") == "BSE" or ".BO" in q.get("symbol", "")]
            
            # Add exchange information
            for q in nse_quotes:
                q["detected_exchange"] = "NSE"
                
            for q in bse_quotes:
                q["detected_exchange"] = "BSE"
                
            # If the requested exchange is NSE, prioritize NSE stocks
            if exchange.upper() == "NSE":
                filtered_quotes = nse_quotes
                # If no NSE stocks found, return BSE stocks
                if not filtered_quotes:
                    filtered_quotes = bse_quotes
            # If the requested exchange is BSE, prioritize BSE stocks
            elif exchange.upper() == "BSE":
                filtered_quotes = bse_quotes
                # If no BSE stocks found, return NSE stocks
                if not filtered_quotes:
                    filtered_quotes = nse_quotes
            else:
                # If no specific exchange, combine NSE and BSE stocks
                filtered_quotes = nse_quotes + bse_quotes
                
            return filtered_quotes
        else:
            logger.error(f"Failed to search stocks: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error searching stocks: {str(e)}")
        return []

def analyze_stock_trend(stock_data, days=30):
    """
    Analyze stock price trend over a period.
    
    Args:
        stock_data (dict): Stock data from fetch_stock_data
        days (int): Number of days to analyze
        
    Returns:
        dict: Analysis results
    """
    try:
        if "error" in stock_data:
            return stock_data
            
        chart_data = stock_data.get("data", {}).get("chart", {}).get("result", [{}])[0]
        timestamps = chart_data.get("timestamp", [])
        
        # Get the close prices
        indicators = chart_data.get("indicators", {})
        quote = indicators.get("quote", [{}])[0]
        close_prices = quote.get("close", [])
        
        if not close_prices or len(close_prices) < 2:
            return {"error": "Insufficient data for analysis"}
            
        # Calculate metrics
        latest_price = close_prices[-1]
        previous_price = close_prices[-2]
        start_price = close_prices[0]
        
        # Calculate percentage changes
        daily_change_pct = ((latest_price - previous_price) / previous_price) * 100
        period_change_pct = ((latest_price - start_price) / start_price) * 100
        
        # Calculate simple moving averages
        sma_5 = np.mean(close_prices[-5:]) if len(close_prices) >= 5 else None
        sma_20 = np.mean(close_prices[-20:]) if len(close_prices) >= 20 else None
        
        # Determine trend
        if period_change_pct > 5:
            trend = "Strong Upward"
            recommendation = "Consider taking profits if already invested. For new investors, wait for a pullback."
        elif period_change_pct > 2:
            trend = "Upward"
            recommendation = "Hold if already invested. For new investors, consider partial position."
        elif period_change_pct > -2:
            trend = "Sideways"
            recommendation = "Hold if already invested. For new investors, consider dollar-cost averaging."
        elif period_change_pct > -5:
            trend = "Downward"
            recommendation = "Hold if long-term investor. For short-term, consider reducing position."
        else:
            trend = "Strong Downward"
            recommendation = "Consider cutting losses if short-term investor. For long-term, potential buying opportunity if fundamentals are strong."

        # Compare with moving averages
        price_vs_sma5 = "above" if latest_price > sma_5 else "below" if sma_5 else "unknown"
        price_vs_sma20 = "above" if latest_price > sma_20 else "below" if sma_20 else "unknown"
        
        # Additional recommendation based on moving averages
        if price_vs_sma5 == "above" and price_vs_sma20 == "above":
            ma_signal = "Bullish"
        elif price_vs_sma5 == "below" and price_vs_sma20 == "below":
            ma_signal = "Bearish"
        elif price_vs_sma5 == "above" and price_vs_sma20 == "below":
            ma_signal = "Potential reversal to upside"
        elif price_vs_sma5 == "below" and price_vs_sma20 == "above":
            ma_signal = "Potential reversal to downside"
        else:
            ma_signal = "Neutral"
            
        return {
            "status": "success",
            "latest_price": round(latest_price, 2),
            "daily_change_percentage": round(daily_change_pct, 2),
            "period_change_percentage": round(period_change_pct, 2),
            "sma_5": round(sma_5, 2) if sma_5 else None,
            "sma_20": round(sma_20, 2) if sma_20 else None,
            "trend": trend,
            "moving_average_signal": ma_signal,
            "recommendation": recommendation
        }
    except Exception as e:
        logger.error(f"Error analyzing stock trend: {str(e)}")
        return {"error": f"Error analyzing stock trend: {str(e)}"}

def analyze_mutual_fund(fund_data, days=30):
    """
    Analyze mutual fund performance over a period.
    
    Args:
        fund_data (dict): Fund data from fetch_mutual_fund_data
        days (int): Number of days to analyze
        
    Returns:
        dict: Analysis results
    """
    try:
        if "error" in fund_data:
            return fund_data
            
        # Extract data
        scheme_name = fund_data.get("meta", {}).get("scheme_name", "Unknown Fund")
        fund_house = fund_data.get("meta", {}).get("fund_house", "Unknown AMC")
        scheme_type = fund_data.get("meta", {}).get("scheme_type", "Unknown Type")
        nav_data = fund_data.get("data", [])
        
        if not nav_data or len(nav_data) < 2:
            return {"error": "Insufficient NAV data for analysis"}
            
        # Extract recent NAVs (sorted by date in descending order)
        recent_navs = nav_data[:min(days, len(nav_data))]
        
        # Calculate metrics
        latest_nav = float(recent_navs[0].get("nav", 0))
        previous_nav = float(recent_navs[1].get("nav", 0))
        
        # Get NAV from 30 days ago or the oldest available if less than 30 days
        start_nav = float(recent_navs[-1].get("nav", 0))
        
        # Calculate percentage changes
        daily_change_pct = ((latest_nav - previous_nav) / previous_nav) * 100
        period_change_pct = ((latest_nav - start_nav) / start_nav) * 100
        
        # Annualized return (simple approximation)
        annual_return_pct = period_change_pct * (365 / min(days, len(recent_navs)))
        
        # Determine trend and recommendation
        if period_change_pct > 5:
            trend = "Strong Upward"
            recommendation = "Consider continuing SIP. Good performance metrics."
        elif period_change_pct > 2:
            trend = "Upward"
            recommendation = "Continue SIP investments. Fund showing positive momentum."
        elif period_change_pct > -2:
            trend = "Sideways"
            recommendation = "Hold SIP investments. Monitor performance in coming weeks."
        elif period_change_pct > -5:
            trend = "Downward"
            recommendation = "Continue SIP for dollar-cost averaging. Review fund fundamentals."
        else:
            trend = "Strong Downward"
            recommendation = "Evaluate fund manager's strategy and performance. Consider researching alternatives while continuing SIP for cost averaging."
            
        return {
            "status": "success",
            "scheme_name": scheme_name,
            "fund_house": fund_house,
            "scheme_type": scheme_type,
            "latest_nav": latest_nav,
            "daily_change_percentage": round(daily_change_pct, 2),
            "period_change_percentage": round(period_change_pct, 2),
            "estimated_annual_return": round(annual_return_pct, 2),
            "trend": trend,
            "recommendation": recommendation
        }
    except Exception as e:
        logger.error(f"Error analyzing mutual fund: {str(e)}")
        return {"error": f"Error analyzing mutual fund: {str(e)}"}

def get_similar_stock_recommendations(symbol, exchange="NSE", count=4, include_both_exchanges=False):
    """
    Get recommendations for similar stocks.
    
    Args:
        symbol (str): Stock symbol
        exchange (str): Stock exchange (NSE or BSE)
        count (int): Number of recommendations to return
        include_both_exchanges (bool): Whether to include stocks from both exchanges
        
    Returns:
        list: List of recommended stocks
    """
    try:
        # Always include both exchanges to provide more options
        include_both_exchanges = True
        
        # First try to find similar stocks based on sector and industry
        all_recommendations = []
        
        # Look up the stock to get its sector/industry
        stock_search = search_stock(symbol, exchange)
        if not stock_search:
            return []
        
        # Get the first match
        target_stock = stock_search[0]
        target_sector = target_stock.get("sector", "")
        target_industry = target_stock.get("industry", "")
        
        # If we don't have sector/industry info, just search more broadly
        if not target_sector and not target_industry:
            # Search using the symbol as a query
            search_results = search_stock(symbol, exchange)
            
            # Filter out the target stock
            filtered_results = [s for s in search_results if s.get("symbol", "").split(".")[0] != symbol]
            
            # Process the search results
            for stock in filtered_results[:count*2]:  # Get more than needed to allow for filtering
                stock_info = {
                    "symbol": stock.get("symbol", "").split(".")[0],
                    "name": stock.get("shortname", stock.get("longname", "Unknown")),
                    "exchange": stock.get("detected_exchange", exchange)
                }
                all_recommendations.append(stock_info)
        else:
            # Perform searches for stocks in the same sector/industry
            sector_results = []
            industry_results = []
            
            # Get more stocks from the same sector
            if target_sector:
                sector_keywords = target_sector.split()
                for keyword in sector_keywords:
                    if len(keyword) > 3:  # Only use meaningful keywords
                        sector_matches = search_stock(keyword, exchange)
                        for match in sector_matches:
                            # Check if it's a different stock
                            if match.get("symbol", "").split(".")[0] != symbol:
                                stock_info = {
                                    "symbol": match.get("symbol", "").split(".")[0],
                                    "name": match.get("shortname", match.get("longname", "Unknown")),
                                    "exchange": match.get("detected_exchange", exchange),
                                    "sector": match.get("sector", ""),
                                    "industry": match.get("industry", "")
                                }
                                if stock_info not in sector_results:
                                    sector_results.append(stock_info)
            
            # Get more stocks from the same industry
            if target_industry:
                industry_keywords = target_industry.split()
                for keyword in industry_keywords:
                    if len(keyword) > 3:  # Only use meaningful keywords
                        industry_matches = search_stock(keyword, exchange)
                        for match in industry_matches:
                            # Check if it's a different stock
                            if match.get("symbol", "").split(".")[0] != symbol:
                                stock_info = {
                                    "symbol": match.get("symbol", "").split(".")[0],
                                    "name": match.get("shortname", match.get("longname", "Unknown")),
                                    "exchange": match.get("detected_exchange", exchange),
                                    "sector": match.get("sector", ""),
                                    "industry": match.get("industry", "")
                                }
                                if stock_info not in industry_results and stock_info not in sector_results:
                                    industry_results.append(stock_info)
            
            # Prioritize industry matches over sector matches
            all_recommendations = industry_results + sector_results
        
        # Ensure we have enough recommendations
        if len(all_recommendations) < count:
            # If we don't have enough recommendations, add some popular stocks
            popular_stocks = [
                {"symbol": "RELIANCE", "name": "Reliance Industries", "exchange": "NSE"},
                {"symbol": "TCS", "name": "Tata Consultancy Services", "exchange": "NSE"},
                {"symbol": "HDFC", "name": "HDFC Bank", "exchange": "NSE"},
                {"symbol": "INFY", "name": "Infosys", "exchange": "NSE"},
                {"symbol": "ITC", "name": "ITC Limited", "exchange": "NSE"},
                {"symbol": "SBIN", "name": "State Bank of India", "exchange": "NSE"},
                {"symbol": "WIPRO", "name": "Wipro", "exchange": "NSE"},
                {"symbol": "ADANIENT", "name": "Adani Enterprises", "exchange": "NSE"},
                {"symbol": "TATAMOTORS", "name": "Tata Motors", "exchange": "NSE"},
                {"symbol": "AXISBANK", "name": "Axis Bank", "exchange": "NSE"}
            ]
            
            # Remove any popular stocks that match our target stock
            filtered_popular = [s for s in popular_stocks if s["symbol"] != symbol]
            
            # Add popular stocks not already in our recommendations
            for stock in filtered_popular:
                if stock not in all_recommendations:
                    all_recommendations.append(stock)
        
        # Remove duplicates by symbol
        symbols_added = set()
        unique_recommendations = []
        for stock in all_recommendations:
            stock_symbol = stock.get("symbol", "")
            if stock_symbol and stock_symbol not in symbols_added:
                symbols_added.add(stock_symbol)
                unique_recommendations.append(stock)
        
        # Get recommendations from other exchange if requested
        if include_both_exchanges:
            other_exchange = "BSE" if exchange.upper() == "NSE" else "NSE"
            
            # Convert our NSE recommendations to their BSE equivalents
            if exchange.upper() == "NSE":
                bse_recommendations = convert_nse_to_bse(unique_recommendations[:count])
                
                # Add BSE recommendations
                for stock in bse_recommendations:
                    if stock.get("symbol", "") and stock not in unique_recommendations:
                        unique_recommendations.append(stock)
            else:
                # Try to find similar stocks on NSE
                nse_recommendations = []
                for stock in unique_recommendations[:count]:
                    symbol = stock.get("symbol", "").replace(".BO", "")
                    if symbol:
                        nse_matches = search_stock(symbol, "NSE")
                        if nse_matches:
                            nse_stock = {
                                "symbol": nse_matches[0].get("symbol", "").split(".")[0],
                                "name": nse_matches[0].get("shortname", nse_matches[0].get("longname", "Unknown")),
                                "exchange": "NSE"
                            }
                            if nse_stock not in nse_recommendations:
                                nse_recommendations.append(nse_stock)
                
                # Add NSE recommendations
                for stock in nse_recommendations:
                    if stock.get("symbol", "") and stock not in unique_recommendations:
                        unique_recommendations.append(stock)
        
        # Return the top count recommendations
        return unique_recommendations[:count*2]  # Return more recommendations for variety
        
    except Exception as e:
        logger.error(f"Error getting stock recommendations: {str(e)}")
        return []
