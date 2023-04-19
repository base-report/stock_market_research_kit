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


def create_trades_table(conn: Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            entry_date TEXT,
            entry_price REAL,
            initial_stop REAL,
            consolidation_days INTEGER,
            adr20 REAL,
            volume20 REAL,
            partial_target_date TEXT,
            partial_target_price REAL,
            partial_target_reached INTEGER,
            exit_date TEXT,
            exit_price REAL,
            exit_reason TEXT,
            days_held INTEGER,
            FOREIGN KEY (symbol) REFERENCES stock_data (symbol)
        );
        """
    )
    conn.commit()


def add_cluster_column_to_trades_table(conn: Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        ALTER TABLE trades ADD COLUMN cluster INTEGER;
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
