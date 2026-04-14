import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data import fetch_data
from indicators import add_indicators
from strategy import generate_signals
from backtest import run_backtest


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Trend Following Dashboard", layout="wide")
st.title("📈 Trend Following Backtest Dashboard")


# =========================
# SIDEBAR - MULTISELECT
# =========================
ticker_options = [

    # EQUITIES
    "AAPL", "TSLA", "MSFT", "GOOGL", "AMZN",
    "^GSPC", "^DJI", "^IXIC", "^NSEI", "^FTSE", "^N225",

    # CRYPTO
    "BTC-USD", "ETH-USD",

    # COMMODITIES
    "GC=F", "SI=F", "CL=F", "NG=F", "HG=F",

    # FOREX
    "USDINR=X", "EURUSD=X", "GBPUSD=X", "USDJPY=X",

    # BONDS
    "^TNX"
]

tickers = st.sidebar.multiselect(
    "Select Assets",
    options=ticker_options,
    default=["AAPL", "BTC-USD", "GC=F"]
)

if len(tickers) == 0:
    st.warning("Please select at least one asset")
    st.stop()


# =========================
# RUN PIPELINE
# =========================

initial_capital = 1_000_000
capital_per_asset = initial_capital / len(tickers)

portfolio_equity = None
last_df = None

for ticker in tickers:
    try:
        df = fetch_data(ticker)
        df = add_indicators(df)
        df = generate_signals(df)

        # 🔥 PASS CAPITAL PER ASSET
        df = run_backtest(df, initial_capital=capital_per_asset)

        last_df = df.copy()

        df_eq = df[['equity']].rename(columns={'equity': ticker})

        if portfolio_equity is None:
            portfolio_equity = df_eq
        else:
            portfolio_equity = portfolio_equity.join(df_eq, how='outer')

    except Exception as e:
        st.warning(f"Skipping {ticker}: {e}")


# =========================
# PORTFOLIO COMBINE
# =========================
portfolio_equity.sort_index(inplace=True)
portfolio_equity = portfolio_equity.ffill()
portfolio_equity.dropna(inplace=True)

portfolio_equity['Total'] = portfolio_equity.sum(axis=1)


# =========================
# CURRENT SIGNAL (LAST ASSET)
# =========================
latest_price = last_df['Close'].iloc[-1]

if last_df['position'].iloc[-1] == 1:
    latest_signal = "LONG"
else:
    latest_signal = "HOLD"

st.subheader("📍 Current Signal (Last Selected Asset)")

colA, colB = st.columns(2)
colA.metric("Signal", latest_signal)
colB.metric("Price", f"{latest_price:,.2f}")


# =========================
# PERFORMANCE METRICS
# =========================
equity = portfolio_equity['Total']

start = equity.iloc[0]
end = equity.iloc[-1]

total_return = (end / start - 1) * 100

years = len(equity) / 252
cagr = ((end / start) ** (1 / years) - 1) * 100

peak = equity.cummax()
drawdown = (equity - peak) / peak
max_drawdown = drawdown.min() * 100

st.subheader("📊 Performance")

col1, col2, col3 = st.columns(3)
col1.metric("Total Return (%)", f"{total_return:.2f}")
col2.metric("CAGR (%)", f"{cagr:.2f}")
col3.metric("Max Drawdown (%)", f"{max_drawdown:.2f}")


# =========================
# EQUITY CURVE
# =========================
st.subheader("📈 Portfolio Equity Curve")

fig = go.Figure()

# Portfolio equity
fig.add_trace(go.Scatter(
    x=portfolio_equity.index,
    y=portfolio_equity['Total'],
    mode='lines',
    name='Portfolio Equity'
))

# Normalized price (last asset)
price_norm = last_df['Close'] / last_df['Close'].iloc[0] * equity.iloc[0]

fig.add_trace(go.Scatter(
    x=last_df.index,
    y=price_norm,
    mode='lines',
    name='Last Asset Price (Normalized)'
))


# =========================
# BUY / SELL MARKERS
# =========================
buy_signals = last_df[last_df['signal'] == 'BUY']
sell_signals = last_df[last_df['signal'] == 'SELL']

fig.add_trace(go.Scatter(
    x=buy_signals.index,
    y=buy_signals['equity'],
    mode='markers',
    name='BUY',
    marker=dict(symbol='triangle-up', size=10)
))

fig.add_trace(go.Scatter(
    x=sell_signals.index,
    y=sell_signals['equity'],
    mode='markers',
    name='SELL',
    marker=dict(symbol='triangle-down', size=10)
))

st.plotly_chart(fig, use_container_width=True)


# =========================
# SIGNAL TABLE
# =========================
st.subheader("📋 Trade Signals (Last Selected Asset)")

signals_df = last_df[last_df['signal'].notna()][['Close', 'signal']]
st.dataframe(signals_df)