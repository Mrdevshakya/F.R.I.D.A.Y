"""
Preprocessing module for the NAV predictor.
Handles data cleaning, normalization, and preparation for analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Setup logging
logger = logging.getLogger(__name__)

def clean_stock_data(stock_data):
    """
    Clean and transform stock data for analysis.
    
    Args:
        stock_data (dict): Stock data from fetch_stock_data
        
    Returns:
        pandas.DataFrame: Cleaned DataFrame or None if error
    """
    try:
        if "error" in stock_data:
            logger.error(f"Cannot clean data with error: {stock_data['error']}")
            return None
            
        chart_data = stock_data.get("data", {}).get("chart", {}).get("result", [{}])[0]
        timestamps = chart_data.get("timestamp", [])
        
        # Convert timestamps to datetime
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        # Get price data
        indicators = chart_data.get("indicators", {})
        quote = indicators.get("quote", [{}])[0]
        
        # Extract price data
        close_prices = quote.get("close", [])
        open_prices = quote.get("open", [])
        high_prices = quote.get("high", [])
        low_prices = quote.get("low", [])
        volumes = quote.get("volume", [])
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes
        })
        
        # Clean NaN values
        df = df.dropna()
        
        # Sort by date
        df = df.sort_values('date')
        
        # Set date as index
        df = df.set_index('date')
        
        return df
    except Exception as e:
        logger.error(f"Error cleaning stock data: {str(e)}")
        return None

def clean_mutual_fund_data(fund_data):
    """
    Clean and transform mutual fund data for analysis.
    
    Args:
        fund_data (dict): Fund data from fetch_mutual_fund_data
        
    Returns:
        pandas.DataFrame: Cleaned DataFrame or None if error
    """
    try:
        if "error" in fund_data:
            logger.error(f"Cannot clean data with error: {fund_data['error']}")
            return None
            
        nav_data = fund_data.get("data", [])
        
        if not nav_data:
            logger.error("No NAV data found")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(nav_data)
        
        # Convert date strings to datetime
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
        
        # Convert NAV strings to float
        df['nav'] = df['nav'].astype(float)
        
        # Sort by date
        df = df.sort_values('date')
        
        # Set date as index
        df = df.set_index('date')
        
        return df
    except Exception as e:
        logger.error(f"Error cleaning mutual fund data: {str(e)}")
        return None

def calculate_returns(df, periods=[1, 7, 30, 90, 180, 365]):
    """
    Calculate returns over different time periods.
    
    Args:
        df (pandas.DataFrame): DataFrame with 'close' or 'nav' column
        periods (list): List of periods in days to calculate returns for
        
    Returns:
        pandas.DataFrame: DataFrame with returns added
    """
    try:
        # Copy DataFrame to avoid modifying original
        result_df = df.copy()
        
        # Determine which column to use (close for stocks, nav for mutual funds)
        value_col = 'close' if 'close' in df.columns else 'nav'
        
        # Calculate returns for each period
        for period in periods:
            col_name = f'return_{period}d'
            result_df[col_name] = result_df[value_col].pct_change(periods=period) * 100
            
        return result_df
    except Exception as e:
        logger.error(f"Error calculating returns: {str(e)}")
        return df

def calculate_technical_indicators(df):
    """
    Calculate technical indicators for analysis.
    Works for both stock and mutual fund data.
    
    Args:
        df (pandas.DataFrame): DataFrame with price/NAV data
        
    Returns:
        pandas.DataFrame: DataFrame with indicators added
    """
    try:
        # Copy DataFrame to avoid modifying original
        result_df = df.copy()
        
        # Determine which column to use (close for stocks, nav for mutual funds)
        value_col = 'close' if 'close' in df.columns else 'nav'
        
        # Calculate Simple Moving Averages
        result_df['SMA_5'] = result_df[value_col].rolling(window=5).mean()
        result_df['SMA_20'] = result_df[value_col].rolling(window=20).mean()
        result_df['SMA_50'] = result_df[value_col].rolling(window=50).mean()
        
        # Calculate Exponential Moving Averages
        result_df['EMA_5'] = result_df[value_col].ewm(span=5, adjust=False).mean()
        result_df['EMA_20'] = result_df[value_col].ewm(span=20, adjust=False).mean()
        
        # Calculate Relative Strength Index (RSI)
        # First, calculate daily changes
        delta = result_df[value_col].diff()
        
        # Get gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss over 14 periods
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        result_df['RSI_14'] = 100 - (100 / (1 + rs))
        
        # Calculate Bollinger Bands (20-day, 2 standard deviations)
        result_df['BB_middle'] = result_df[value_col].rolling(window=20).mean()
        result_df['BB_upper'] = result_df['BB_middle'] + (result_df[value_col].rolling(window=20).std() * 2)
        result_df['BB_lower'] = result_df['BB_middle'] - (result_df[value_col].rolling(window=20).std() * 2)
        
        # Calculate MACD (Moving Average Convergence Divergence)
        result_df['MACD'] = result_df[value_col].ewm(span=12, adjust=False).mean() - result_df[value_col].ewm(span=26, adjust=False).mean()
        result_df['MACD_signal'] = result_df['MACD'].ewm(span=9, adjust=False).mean()
        result_df['MACD_histogram'] = result_df['MACD'] - result_df['MACD_signal']
        
        return result_df
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {str(e)}")
        return df

def prepare_prediction_data(df, lookback_days=30):
    """
    Prepare data for prediction models.
    
    Args:
        df (pandas.DataFrame): DataFrame with price/NAV data and indicators
        lookback_days (int): Number of days to include in analysis
        
    Returns:
        pandas.DataFrame: DataFrame ready for prediction
    """
    try:
        # Get most recent data
        recent_df = df.iloc[-lookback_days:].copy() if len(df) > lookback_days else df.copy()
        
        # Fill any missing values with forward fill then backward fill
        recent_df = recent_df.fillna(method='ffill').fillna(method='bfill')
        
        return recent_df
    except Exception as e:
        logger.error(f"Error preparing prediction data: {str(e)}")
        return df
