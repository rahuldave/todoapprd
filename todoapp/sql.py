import sqlite3

from dotenv import dotenv_values


def get_db(dbfile):
    db = sqlite3.connect(dbfile)
    db.row_factory = sqlite3.Row
    return db


def unget_db(db):
    db.close()


def create_db(dbfile):
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
    config = dotenv_values(".env")
    create_db(config["DATABASE_FILE"])
