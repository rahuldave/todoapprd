from typing import Any

import pytest

from todoapp.app import create_app
from todoapp.sql import create_db, unget_db


def pytest_configure(config: Any) -> None:
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")


@pytest.fixture(scope="session")
def db_setup():
    """Initial database setup, runs once per session."""
    conn = create_db(":memory:")  # Initialize the database schema

    cursor = conn.cursor()
    # Set up categories
    cursor.execute("INSERT INTO categories (name) VALUES ('Work')")
    cursor.execute("INSERT INTO categories (name) VALUES ('Home')")

    # Set up todos
    cursor.execute(
        "INSERT INTO todos (task, done, category_id) VALUES ('Task 1', 0, 1)"
    )
    cursor.execute(
        "INSERT INTO todos (task, done, category_id) VALUES ('Task 2', 1, 2)"
    )
    conn.commit()

    yield conn

    unget_db(conn)


@pytest.fixture
def dbapp(db_setup, request):
    """Function-scoped fixture to provide a clean database state for each test."""
    marker = request.node.get_closest_marker("e2e")
    if marker:
        # For E2E tests, create a new function-scoped database
        conn = create_db(":memory:")

        cursor = conn.cursor()
        # Copy data from session-scoped setup
        setup_cursor = db_setup.cursor()
        for table in ["categories", "todos"]:
            setup_cursor.execute(f"SELECT * FROM {table}")
            rows = setup_cursor.fetchall()
            cursor.executemany(
                f"INSERT INTO {table} VALUES ({','.join(['?' for _ in rows[0]])})", rows
            )

        conn.commit()
        yield conn
        unget_db(conn)
    else:
        # For non-E2E tests, use the session-scoped database
        yield db_setup


@pytest.fixture
def app(dbapp):  # Add the db fixture as an argument
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "DATABASE_FILE": ":memory:",  # not needed but keeping for documentation
            "db": dbapp,  # Add the db connection to the app config
        }
    )
    with app.app_context():
        # Overriding the open_db function to return the session-scoped db fixture
        # otherwise open_db will try and call the filesystem path database and set it
        # in app_config
        def override_open_db(app):
            return app.config["db"]

        app.open_db = override_open_db

        # Override the teardown function to prevent closing the db connection
        def noop_teardown_db(e=None):
            pass

        app.teardown_appcontext_funcs = [noop_teardown_db]
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
