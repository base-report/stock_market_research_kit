import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sqlite3
import json
from dataclasses import asdict
from alive_progress import alive_bar
from stock_market_research_kit.backtest import backtest

DATABASE_PATH = "stock_market_research.db"

# Connect to the SQLite database
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()


# Function to store trades in the trades table
def store_trades(symbol, trades, conn):
    cursor = conn.cursor()
    for trade in trades:
        flat_trade_data = trade.to_db_format(symbol)

        try:
            cursor.execute(
                """
                INSERT INTO trades (symbol, entry_date, entry_price, initial_stop, consolidation_days,
                                    adr20, volume20, partial_target_date, partial_target_price,
                                    partial_target_reached, exit_date, exit_price, exit_reason, days_held)
                VALUES (:symbol, :entry_date, :entry_price, :initial_stop, :consolidation_days,
                        :adr20, :volume20, :partial_target_date, :partial_target_price,
                        :partial_target_reached, :exit_date, :exit_price, :exit_reason, :days_held);
                """,
                flat_trade_data,
            )
        except sqlite3.ProgrammingError as e:
            print(f"Error inserting trade data for symbol {symbol}: {e}")
            print(f"Problematic trade data: {trade}")

    conn.commit()


# Backtest worker function
def backtest_worker(symbol, daily_data_str):
    if daily_data_str is not None:
        daily_data = json.loads(daily_data_str)
        trades = backtest(daily_data)
        with sqlite3.connect(DATABASE_PATH) as conn:
            store_trades(symbol, trades, conn)


def main():
    # Fetch symbols and daily data from the stock_data table
    c.execute("SELECT symbol, daily FROM stock_data;")
    rows = c.fetchall()

    # Run backtest to save trades to the database
    with alive_bar(len(rows), title="Backtesting") as bar:
        for symbol, daily_data_str in rows:
            backtest_worker(symbol, daily_data_str)
            bar()

    # Close the main database connection
    conn.close()


if __name__ == "__main__":
    main()
