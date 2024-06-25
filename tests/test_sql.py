# test_sql.py
import pytest
import sqlite3
from todoapp.sql import get_db, unget_db, create_db

@pytest.fixture
def db():
    conn = create_db(":memory:")  # Initialize the database schema
    yield conn
    unget_db(conn)

def test_get_db(db):
    assert db is not None
    assert isinstance(db, sqlite3.Connection)

def test_create_db():
    conn = create_db(":memory:")

    # Check if tables are created
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories';")
    categories_table = cursor.fetchone()
    assert categories_table is not None

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos';")
    todos_table = cursor.fetchone()
    assert todos_table is not None

    unget_db(conn)

def test_insert_category(db):
    cursor = db.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES ('Work')")
    db.commit()

    last_id = cursor.lastrowid
    assert last_id is not None
    assert last_id > 0

def test_insert_todo_with_foreign_key(db):
    cursor = db.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES ('Home')")
    db.commit()

    category_id = cursor.lastrowid
    cursor.execute("INSERT INTO todos (task, done, category_id) VALUES ('Clean the house', 0, ?)", (category_id,))
    db.commit()

    last_id = cursor.lastrowid
    assert last_id is not None
    assert last_id > 0

def test_query_categories(db):
    cursor = db.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES ('Work')")
    db.commit()

    cursor.execute("SELECT * FROM categories WHERE name='Work'")
    category = cursor.fetchone()

    assert category is not None
    assert category['name'] == 'Work'

def test_query_todos(db):
    cursor = db.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES ('Home')")
    db.commit()

    cursor.execute("INSERT INTO todos (task, done, category_id) VALUES ('Clean the house', 0, 1)")
    db.commit()

    cursor.execute("SELECT * FROM todos WHERE task='Clean the house'")
    todo = cursor.fetchone()

    assert todo is not None
    assert todo['task'] == 'Clean the house'
    assert todo['done'] == 0
    assert todo['category_id'] == 1

def test_unget_db(db):
    conn = get_db(":memory:")
    unget_db(conn)

    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")
