from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    todos = db.relationship('Todo', backref='category', lazy=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(120), nullable=False)
    done = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

@app.route('/')
def index():
    return render_template('todos.html')

@app.route('/todos', methods=['GET', 'POST'])
def manage_todos():
    if request.method == 'POST':
        data = request.json
        new_todo = Todo(task=data['task'], done=False, category_id=data['category_id'])
        db.session.add(new_todo)
        db.session.commit()
        return jsonify(new_todo.id), 201

    todos = Todo.query.all()
    return jsonify([{'id': todo.id, 'task': todo.task, 'done': todo.done, 'category_id': todo.category_id} for todo in todos])

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        data = request.json
        new_category = Category(name=data['name'])
        db.session.add(new_category)
        db.session.commit()
        return jsonify(new_category.id), 201

    categories = Category.query.all()
    return jsonify([{'id': category.id, 'name': category.name} for category in categories])

@app.route('/toggle-todo/<int:todo_id>', methods=['POST'])
def toggle_todo(todo_id):
    todo = Todo.query.get(todo_id)
    todo.done = not todo.done
    db.session.commit()
    return jsonify(todo.done), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
