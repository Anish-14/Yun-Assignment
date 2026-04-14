import yfinance as yf
import pandas as pd


def fetch_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    df = yf.download(
        ticker,
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    # 🔥 FORCE FLATTEN columns (robust fix)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

    df.dropna(inplace=True)
    df.sort_index(inplace=True)

    return df