from sqlite3 import Connection
from typing import Optional, Tuple, Union

from dotenv import dotenv_values
from flask import Flask, Response, jsonify, render_template, request
from pydantic import BaseModel, ValidationError

from todoapp.sql import get_db, unget_db


class CategoryIncoming(BaseModel):
    "A Category Dataclass"

    name: str  # the title of the wikipedia page


class TodoIncoming(BaseModel):
    "A Todo Dataclass"

    task: str  # the text of the task
    category_id: int  # the category ID of the task


def open_db(app: Flask) -> Connection:
    if "db" not in app.config:
        db = get_db(app.config["DATABASE_FILE"])
        app.config["db"] = db
        return db
    return app.config["db"]


def create_app() -> Flask:
    config = dotenv_values(".env")
    app = Flask(__name__, template_folder=config["TEMPLATE_FOLDER"])
    app.config["EXPLAIN_TEMPLATE_LOADING"] = True
    app.config["DEBUG"] = True if (config["DEBUG"] == "True") else False
    app.config["DATABASE_FILE"] = config["DATABASE_FILE"]

    @app.route("/")
    def index() -> str:
        return render_template("todos.html")

    @app.route("/todos", methods=["GET", "POST"])
    def manage_todos() -> Union[Response, Tuple[Response, int]]:
        conn = open_db(app)
        if request.method == "POST":
            data = request.json
            if data is None:
                return jsonify({"error": "No data provided"}), 400
            try:
                todo = TodoIncoming(**data)
            except ValidationError as e:
                return jsonify(e.errors()), 422
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO todos (task, done, category_id) VALUES (?, ?, ?)",
                (todo.task, False, todo.category_id),
            )
            conn.commit()
            return jsonify(cursor.lastrowid), 201

        todos = conn.execute("SELECT * FROM todos").fetchall()
        # Should one be rturning todos insted of dicts? For Validation Purposes.
        return jsonify([dict(todo) for todo in todos])

    @app.route("/categories", methods=["GET", "POST"])
    def manage_categories() -> Union[Response, Tuple[Response, int]]:
        conn = open_db(app)
        if request.method == "POST":
            data = request.json
            if data is None:
                return jsonify({"error": "No data provided"}), 400
            try:
                cat = CategoryIncoming(**data)
            except ValidationError as e:
                return jsonify(e.errors()), 422
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (cat.name,))
            conn.commit()
            return jsonify(cursor.lastrowid), 201

        categories = conn.execute("SELECT * FROM categories").fetchall()
        return jsonify([dict(category) for category in categories])

    @app.route("/toggle-todo/<int:todo_id>", methods=["POST"])
    def toggle_todo(todo_id: int) -> Tuple[Response, int]:
        conn = open_db(app)
        todo = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        done = not todo["done"]
        conn.execute("UPDATE todos SET done = ? WHERE id = ?", (done, todo_id))
        conn.commit()
        return jsonify(done), 200

    @app.teardown_appcontext
    def close_db(e: Optional[BaseException] = None) -> None:
        db = app.config.pop("db", None)
        if db is not None:
            unget_db(db)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
