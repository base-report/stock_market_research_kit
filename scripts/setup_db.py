import sqlite3
from sqlite3 import Connection


def create_database(database_name: str) -> Connection:
    conn = sqlite3.connect(database_name)
    return conn


def create_stock_data_table(conn: Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stock_data (
            symbol TEXT NOT NULL PRIMARY KEY,
            exchange TEXT,
            sector TEXT,
            industry TEXT,
            delisted INTEGER,
            daily BLOB
        );
        """
    )
    conn.commit()


def main():
    db_name = "stock_market_research.db"
    conn = create_database(db_name)
    create_stock_data_table(conn)
    print("Database created successfully")
    conn.close()


if __name__ == "__main__":
    main()
