import os
import json
import sqlite3
import requests
from alive_progress import alive_bar
from dotenv import load_dotenv
import concurrent.futures

load_dotenv()

FMP_API_KEY = os.environ["FMP_API_KEY"]
DB_PATH = "stock_market_research.db"


def connect_to_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_stocks_from_db():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM stock_data")
    return cur.fetchall()


def fetch_timeseries_data(stock):
    symbol = stock["symbol"]
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?from=1950-01-01&apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data for {symbol}, status code: {response.status_code}")
        return
    data = response.json()

    if "historical" not in data:
        print(f"No historical data found for {symbol}")
        return

    timeseries_data = []

    for daily_data in data["historical"][::-1]:
        date = daily_data["date"]
        open_price = daily_data["open"]
        high = daily_data["high"]
        low = daily_data["low"]
        close = daily_data["close"]
        adj_close = daily_data["adjClose"]
        volume = daily_data["volume"]

        if close == 0:
            continue

        adj_open = round(open_price * (adj_close / close), 4)
        adj_high = round(high * (adj_close / close), 4)
        adj_low = round(low * (adj_close / close), 4)
        adj_close = round(adj_close, 4)

        timeseries_data.append([adj_open, adj_high, adj_low, adj_close, volume, date])

    update_stock_data(timeseries_data, symbol)


def update_stock_data(timeseries_data, symbol):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE stock_data SET daily = ? WHERE symbol = ?",
        (json.dumps(timeseries_data), symbol),
    )
    conn.commit()


def fetch_and_save_timeseries_data_for_all_stocks(stocks):
    max_workers = 10

    with alive_bar(len(stocks), title="Downloading timeseries data...") as bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(fetch_timeseries_data, stock) for stock in stocks
            ]

            for future in concurrent.futures.as_completed(futures):
                bar()
                future.result()  # Raise any exceptions from the worker threads.


def main():
    stocks = get_stocks_from_db()
    fetch_and_save_timeseries_data_for_all_stocks(stocks)


if __name__ == "__main__":
    main()
