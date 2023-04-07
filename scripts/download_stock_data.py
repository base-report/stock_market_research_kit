import csv
import os
import requests
import sqlite3
from dotenv import load_dotenv
from io import StringIO

load_dotenv()
FMP_API_KEY = os.environ["FMP_API_KEY"]
DATABASE_PATH = "stock_market_research.db"

API_URL = f"https://financialmodelingprep.com/api/v4/profile/all?apikey={FMP_API_KEY}"
VALID_EXCHANGES = {"AMEX", "NASDAQ", "NYSE"}


def fetch_stock_data():
    response = requests.get(API_URL)
    response.raise_for_status()
    return csv.DictReader(StringIO(response.text))


def insert_stock_data(connection, stock_data):
    cursor = connection.cursor()
    for row in stock_data:
        if row["exchangeShortName"] not in VALID_EXCHANGES:
            continue

        delisted = 1 if row["isActivelyTrading"].lower() == "false" else 0

        cursor.execute(
            "INSERT OR IGNORE INTO stock_data (symbol, exchange, sector, industry, delisted) VALUES (?, ?, ?, ?, ?)",
            (
                row["Symbol"],
                row["exchangeShortName"],
                row["sector"],
                row["industry"],
                delisted,
            ),
        )
    connection.commit()


def main():
    connection = sqlite3.connect(DATABASE_PATH)
    stock_data = fetch_stock_data()
    insert_stock_data(connection, stock_data)
    print("Inserted stock data")
    connection.close()


if __name__ == "__main__":
    main()
