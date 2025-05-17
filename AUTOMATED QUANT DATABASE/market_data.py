from sys import argv
import pandas as pd
import yfinance as yf
import sqlite3
from pandas.tseries.offsets import BDay



def get_stock_data(symbol, start, end):
    try:
        data = yf.download(symbol, start=start, end=end, progress=False)
        if data.empty:
            raise ValueError("No data fetched (possibly due to non-trading day or symbol error).")
        data.reset_index(inplace=True)
        data.rename(columns={
            "Date": "date",
            "Open": "open",
            "Low": "low",
            "High": "high",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume"  
        }, inplace=True)
        data['symbol'] = symbol
        return data
    except Exception as e:
        print(f"[Error] Failed to fetch {symbol}: {e}")
        return pd.DataFrame()


def save_data_range(symbol, start, end, con):
    data = get_stock_data(symbol, start, end)
    if not data.empty:
        data.to_sql("stock_data", con, if_exists="append", index=False)
        print(f"{symbol} saved between {start} and {end}")
    else:
        print(f"No data saved for {symbol}.")


def save_last_trading_session(symbol, con):
    last_trading_day = pd.Timestamp.today() - BDay(1)
    next_day = last_trading_day + pd.Timedelta(days=1)
    data = get_stock_data(symbol, last_trading_day, next_day)
    if not data.empty:
        data.to_sql("stock_data", con, if_exists="append", index=False)
        print(f"{symbol} saved for {last_trading_day.date()}")
    else:
        print(f"No data available for {symbol} on {last_trading_day.date()}")


if __name__ == "__main__":
    con = sqlite3.connect("market_data.sqlite")

    if len(argv) < 3:
        print("Usage:")
        print("  python market_data.py bulk SYMBOL START_DATE END_DATE")
        print("  python market_data.py last SYMBOL")
    elif argv[1] == "bulk" and len(argv) == 5:
        _, _, symbol, start, end = argv
        save_data_range(symbol, start, end, con)
    elif argv[1] == "last" and len(argv) == 3:
        _, _, symbol = argv
        save_last_trading_session(symbol, con)
    else:
        print("Invalid arguments. Use 'bulk SYMBOL START END' or 'last SYMBOL'")
