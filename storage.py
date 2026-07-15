import sqlite3
from pathlib import Path


DB_PATH = Path("price_monitor.db")


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS scrape_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS price_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scrape_run_id INTEGER NOT NULL,
            competitor TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT NOT NULL,
            in_stock INTEGER NOT NULL,
            stock_text TEXT NOT NULL,
            rating INTEGER,
            observed_at TEXT NOT NULL,
            FOREIGN KEY (scrape_run_id) REFERENCES scrape_runs (id)
        )
        """
    )
    connection.commit()


def create_scrape_run(connection: sqlite3.Connection, created_at: str) -> int:
    cursor = connection.execute(
        "INSERT INTO scrape_runs (created_at) VALUES (?)",
        (created_at,),
    )
    connection.commit()
    return int(cursor.lastrowid)


def save_snapshots(connection: sqlite3.Connection, scrape_run_id: int, snapshots: list[dict]) -> None:
    connection.executemany(
        """
        INSERT INTO price_snapshots (
            scrape_run_id,
            competitor,
            title,
            url,
            price,
            currency,
            in_stock,
            stock_text,
            rating,
            observed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                scrape_run_id,
                snapshot["competitor"],
                snapshot["title"],
                snapshot["url"],
                snapshot["price"],
                snapshot["currency"],
                int(snapshot["in_stock"]),
                snapshot["stock_text"],
                snapshot["rating"],
                snapshot["observed_at"],
            )
            for snapshot in snapshots
        ],
    )
    connection.commit()


def get_latest_run_ids(connection: sqlite3.Connection, limit: int = 2) -> list[int]:
    rows = connection.execute(
        """
        SELECT id
        FROM scrape_runs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [int(row["id"]) for row in rows]


def get_snapshots_for_run(connection: sqlite3.Connection, scrape_run_id: int) -> list[dict]:
    rows = connection.execute(
        """
        SELECT *
        FROM price_snapshots
        WHERE scrape_run_id = ?
        ORDER BY title
        """,
        (scrape_run_id,),
    ).fetchall()
    return [dict(row) for row in rows]
