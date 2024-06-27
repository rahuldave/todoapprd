import sqlite3
from sqlite3 import Connection

from todoapp.config import get_configs


def get_db(dbfile: str) -> Connection:
    "Get a connection to the database"
    db = sqlite3.connect(dbfile)
    db.row_factory = sqlite3.Row
    return db


def unget_db(db: Connection) -> None:
    "Close the connection to the database"
    db.close()


def create_db(dbfile: str) -> Connection:
    "Get a connection to the database and create the tables"
    db = get_db(dbfile)
    db.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            done BOOLEAN NOT NULL CHECK (done IN (0, 1)),
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    """)
    db.commit()
    return db


if __name__ == "__main__":
    config = get_configs()
    if config:
        dbfile = config["DATABASE_FILE"]
        print("Creating database...", dbfile)
        if dbfile:
            create_db(dbfile)
