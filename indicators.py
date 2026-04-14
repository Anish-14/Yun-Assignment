import pandas as pd
import numpy as np


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df.copy()

    # EMA
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA100'] = df['Close'].ewm(span=100, adjust=False).mean()

    # Breakouts (no lookahead)
    df['50_high'] = df['High'].rolling(50).max().shift(1)
    df['50_low'] = df['Low'].rolling(50).min().shift(1)

    # True Range (vectorized, no temp cols)
    prev_close = df['Close'].shift(1)

    df['TR'] = np.maximum.reduce([
        df['High'] - df['Low'],
        (df['High'] - prev_close).abs(),
        (df['Low'] - prev_close).abs()
    ])

    # ATR (Wilder)
    df['ATR'] = df['TR'].ewm(alpha=1/20, adjust=False).mean()

    df.drop(columns=['TR'], inplace=True)

    df.dropna(inplace=True)

    return df