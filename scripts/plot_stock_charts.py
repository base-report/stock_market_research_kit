import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sqlite3
import json
from datetime import datetime
from stock_market_research_kit.chart import plot_and_save_chart
from concurrent.futures import ThreadPoolExecutor
from alive_progress import alive_bar

DATABASE_PATH = "stock_market_research.db"
FOLDER_PATH = "./data/images/all"


def get_all_trades(cursor):
    cursor.execute("SELECT * FROM trades")
    return cursor.fetchall()


def get_all_daily_data(cursor):
    cursor.execute("SELECT symbol, daily FROM stock_data where daily is not null")
    daily_data = {}
    for row in cursor.fetchall():
        symbol, data = row
        daily_data[symbol] = json.loads(data)
    return daily_data


def get_past_200_candles_before_entry(daily_data, entry_date):
    entry_date_dt = datetime.strptime(entry_date, "%Y-%m-%d")
    index = next(
        (
            i
            for i, candle in enumerate(daily_data)
            if datetime.strptime(candle[5], "%Y-%m-%d") >= entry_date_dt
        ),
        None,
    )
    return daily_data[max(0, index - 200) : index]


def process_trade(trade, daily_data):
    # Get the entry_date of the trade
    id = trade[0]
    symbol = trade[1]
    entry_date = trade[2]

    # Get the past 200 candles before the entry date of the trade
    past_200_candles = get_past_200_candles_before_entry(daily_data[symbol], entry_date)

    # Continue processing the candles
    plot_and_save_chart(FOLDER_PATH, symbol, id, past_200_candles)


def main():
    # Connect to your SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get all trades
    print("Getting all trades...")
    trades = get_all_trades(cursor)

    # Get all daily data at once
    print("Getting all daily data (this may take a moment) ...")
    all_daily_data = get_all_daily_data(cursor)

    # Use ThreadPoolExecutor to manage workers
    with ThreadPoolExecutor(max_workers=10) as executor:
        with alive_bar(len(trades), title="Processing trades") as bar:
            futures = [
                executor.submit(process_trade, trade, all_daily_data)
                for trade in trades
            ]

            for future in futures:
                future.result()
                bar()

    # Close the main database connection
    conn.close()


if __name__ == "__main__":
    main()
