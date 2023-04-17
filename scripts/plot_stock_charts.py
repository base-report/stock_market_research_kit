import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import sqlite3
import json
from datetime import datetime
from alive_progress import alive_bar
from stock_market_research_kit.chart import plot_and_save_chart

DATABASE_PATH = "stock_market_research.db"


# Folder name
folder_path = "./data/images"


def get_distinct_symbols(cursor):
    cursor.execute("SELECT DISTINCT symbol FROM trades")
    return [row[0] for row in cursor.fetchall()]


def get_daily_data_for_symbol(cursor, symbol):
    cursor.execute("SELECT daily FROM stock_data WHERE symbol = ?", (symbol,))
    daily_data = cursor.fetchone()[0]
    return json.loads(daily_data)


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


def process_symbol(symbol, cursor):
    # Get daily data for the symbol from the stock_data table
    daily_data = get_daily_data_for_symbol(cursor, symbol)

    # Get all trades for the symbol
    cursor.execute("SELECT * FROM trades WHERE symbol = ?", (symbol,))
    trades = cursor.fetchall()

    for trade in trades:
        # Get the entry_date of the trade
        id = trade[0]
        symbol = trade[1]
        entry_date = trade[2]

        # Get the past 200 candles before the entry date of the trade
        past_200_candles = get_past_200_candles_before_entry(daily_data, entry_date)

        # Continue processing the candles
        plot_and_save_chart(folder_path, symbol, id, past_200_candles)


def main():
    # Get all distinct symbols from the trades table
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    symbols = get_distinct_symbols(cursor)

    with alive_bar(len(symbols), title="Plotting stock charts") as bar:
        for symbol in symbols:
            process_symbol(symbol, cursor)
            bar()

    # Close the main database connection
    conn.close()


if __name__ == "__main__":
    main()
