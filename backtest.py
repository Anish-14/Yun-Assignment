import pandas as pd


def run_backtest(df: pd.DataFrame, initial_capital=1_000_000, risk_per_trade=0.002):

    df = df.copy()

    capital = initial_capital
    position = 0
    entry_price = 0
    shares = 0

    equity_curve = []

    for i in range(len(df)):

        row = df.iloc[i]

        # =====================
        # ENTRY
        # =====================
        if row['signal'] == 'BUY' and position == 0:

            # Position sizing based on ATR
            risk_amount = capital * risk_per_trade
            shares = risk_amount / row['ATR']

            entry_price = row['Close']
            position = 1

        # =====================
        # EXIT
        # =====================
        elif row['signal'] == 'SELL' and position == 1:

            pnl = shares * (row['Close'] - entry_price)
            capital += pnl

            position = 0
            shares = 0

        # =====================
        # MARK-TO-MARKET EQUITY
        # =====================
        if position == 1:
            current_value = shares * (row['Close'] - entry_price)
            equity = capital + current_value
        else:
            equity = capital

        equity_curve.append(equity)

    df['equity'] = equity_curve

    return df