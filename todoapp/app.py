from flask import Flask, request, jsonify, render_template, g
from todoapp.sql import  get_db, unget_db
from dotenv import dotenv_values

def open_db(app):
    if 'db' not in app.config:
        app.config['db'] = get_db(app.config['DATABASE_FILE'])
    return app.config['db']


def create_app():
    config = dotenv_values(".env")
    app = Flask(__name__, template_folder=config['TEMPLATE_FOLDER'])
    app.config['EXPLAIN_TEMPLATE_LOADING'] = True
    app.config['DEBUG'] = True if (config['DEBUG'] == 'True') else False
    app.config['DATABASE_FILE'] = config['DATABASE_FILE']

    @app.route('/')
    def index():
        return render_template('todos.html')

    @app.route('/todos', methods=['GET', 'POST'])
    def manage_todos():
        conn = open_db(app)
        if request.method == 'POST':
            data = request.json
            cursor = conn.cursor()
            cursor.execute("INSERT INTO todos (task, done, category_id) VALUES (?, ?, ?)",
                            (data['task'], False, data['category_id']))
            conn.commit()
            return jsonify(cursor.lastrowid), 201

        todos = conn.execute('SELECT * FROM todos').fetchall()
        return jsonify([dict(todo) for todo in todos])

    @app.route('/categories', methods=['GET', 'POST'])
    def manage_categories():
        conn = open_db(app)
        if request.method == 'POST':
            data = request.json
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (data['name'],))
            conn.commit()
            return jsonify(cursor.lastrowid), 201

        categories = conn.execute('SELECT * FROM categories').fetchall()
        return jsonify([dict(category) for category in categories])

    @app.route('/toggle-todo/<int:todo_id>', methods=['POST'])
    def toggle_todo(todo_id):
        conn = open_db(app)
        todo = conn.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
        done = not todo['done']
        conn.execute('UPDATE todos SET done = ? WHERE id = ?', (done, todo_id))
        conn.commit()
        return jsonify(done), 200

    @app.teardown_appcontext
    def close_db(e=None):
        db = app.config.pop("db", None)
        if db is not None:
            unget_db(db)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')
