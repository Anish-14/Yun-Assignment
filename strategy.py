import pandas as pd

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # Initialize columns
    df['position'] = 0
    df['signal'] = None

    in_position = False
    entry_price = 0
    highest_price = 0

    for i in range(len(df)):

        row = df.iloc[i]

        # =====================
        # ENTRY CONDITION
        # =====================
        if not in_position:
            if (row['EMA50'] > row['EMA100']) and (row['Close'] > row['50_high']):
                
                in_position = True
                entry_price = row['Close']
                highest_price = row['Close']

                df.at[df.index[i], 'position'] = 1
                df.at[df.index[i], 'signal'] = 'BUY'

        # =====================
        # EXIT CONDITION
        # =====================
        else:
            # update highest price
            highest_price = max(highest_price, row['Close'])

            trailing_stop = highest_price - 3 * row['ATR']

            if row['Close'] < trailing_stop:
                in_position = False

                df.at[df.index[i], 'position'] = 0
                df.at[df.index[i], 'signal'] = 'SELL'

            else:
                df.at[df.index[i], 'position'] = 1

    return df