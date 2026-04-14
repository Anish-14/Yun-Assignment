import pandas as pd
import matplotlib.pyplot as plt

from data import fetch_data
from indicators import add_indicators
from strategy import generate_signals
from backtest import run_backtest

# =========================
# DISPLAY SETTINGS
# =========================
pd.set_option('display.float_format', '{:,.2f}'.format)


# =========================
# 1. FETCH + PROCESS DATA
# =========================
df = fetch_data("AAPL")   # change ticker if needed
df = add_indicators(df)
df = generate_signals(df)
df = run_backtest(df)


# =========================
# 2. BASIC OUTPUT
# =========================
print("\n===== LAST 20 ROWS =====")
print(df[['Close', 'signal', 'position', 'equity']].tail(20))


# =========================
# 3. SIGNAL CHECK
# =========================
buy_count = (df['signal'] == 'BUY').sum()
sell_count = (df['signal'] == 'SELL').sum()

print("\n===== SIGNAL COUNT =====")
print(f"BUY signals: {buy_count}")
print(f"SELL signals: {sell_count}")

print("\n===== ALL SIGNALS =====")
print(df[df['signal'].notna()][['Close', 'signal']])


# =========================
# 4. STRATEGY VALIDATION
# =========================
condition = (df['EMA50'] > df['EMA100']) & (df['Close'] > df['50_high'])
print("\nValid Entry Conditions:", condition.sum())


# =========================
# 5. PERFORMANCE METRICS
# =========================
start = df['equity'].iloc[0]
end = df['equity'].iloc[-1]

total_return = (end / start - 1) * 100

# CAGR
years = len(df) / 252
cagr = ((end / start) ** (1 / years) - 1) * 100

# Drawdown
df['peak'] = df['equity'].cummax()
df['drawdown'] = (df['equity'] - df['peak']) / df['peak']
max_drawdown = df['drawdown'].min() * 100

print("\n===== PERFORMANCE =====")
print(f"Start Capital: {start:,.2f}")
print(f"End Capital: {end:,.2f}")
print(f"Total Return: {total_return:.2f}%")
print(f"CAGR: {cagr:.2f}%")
print(f"Max Drawdown: {max_drawdown:.2f}%")


# =========================
# 6. EQUITY CURVE PLOT
# =========================
plt.figure()
plt.plot(df['equity'])
plt.title("Equity Curve")
plt.xlabel("Time")
plt.ylabel("Portfolio Value")
plt.show()