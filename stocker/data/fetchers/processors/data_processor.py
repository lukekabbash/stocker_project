import pandas as pd
import numpy as np

def process_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process stock data by adding various technical indicators.

    This function computes several technical indicators for stock analysis, handling potential
    division by zero issues and ensuring the function works well with the rest of the application.

    Parameters:
    df (pd.DataFrame): DataFrame containing stock data with columns 'Close', 'High', 'Low', 'Volume'.

    Returns:
    pd.DataFrame: DataFrame with added technical indicators.

    Raises:
    ValueError: If required columns are missing from the input DataFrame.
    """
    if df.empty:
        return df
    
    # Check for required columns
    required_columns = ['Close', 'High', 'Low', 'Volume']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Missing required columns in DataFrame: {', '.join(set(required_columns) - set(df.columns))}")

    # Add Simple Moving Average
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Add Exponential Moving Average
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    
    # Relative Strength Index (RSI)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan).fillna(1e-8)  # Avoid division by zero
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['stddev_20'] = df['Close'].rolling(window=20).std()
    df['Upper_BB'] = df['SMA_20'] + (df['stddev_20'] * 2)
    df['Lower_BB'] = df['SMA_20'] - (df['stddev_20'] * 2)
    
    # MACD - Moving Average Convergence Divergence
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Volume Indicators
    df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
    
    # Stochastic Oscillator
    low_14 = df['Low'].rolling(window=14).min()
    high_14 = df['High'].rolling(window=14).max()
    df['%K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14 + 1e-8))  # Avoid division by zero
    df['%D'] = df['%K'].rolling(window=3).mean()
    
    # Additional Indicators
    
    # Average True Range (ATR)
    df['TR'] = np.maximum(df['High'] - df['Low'], 
                          np.abs(df['High'] - df['Close'].shift(1)), 
                          np.abs(df['Low'] - df['Close'].shift(1)))
    df['ATR'] = df['TR'].rolling(window=14).mean()
    
    # Commodity Channel Index (CCI)
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    df['CCI'] = (tp - tp.rolling(window=20).mean()) / (0.015 * tp.rolling(window=20).std())
    
    # Money Flow Index (MFI)
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    raw_money_flow = typical_price * df['Volume']
    flow_positive = raw_money_flow.where(raw_money_flow > raw_money_flow.shift(1), 0)
    flow_negative = raw_money_flow.where(raw_money_flow < raw_money_flow.shift(1), 0)
    money_ratio = flow_positive.rolling(window=14).sum() / flow_negative.rolling(window=14).sum().replace(0, np.nan).fillna(1e-8)
    df['MFI'] = 100 - (100 / (1 + money_ratio))
    
    # Williams %R
    df['Williams_%R'] = -100 * ((high_14 - df['Close']) / (high_14 - low_14 + 1e-8))
    