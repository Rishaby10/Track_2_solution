from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import logging

# Initialize Flask app
app = Flask(__name__)

# Set up database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Todo Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    completed = db.Column(db.Boolean, default=False)

    def __init__(self, title, description, completed):
        self.title = title
        self.description = description
        self.completed = completed

# Todo Schema
class TodoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Todo
    id = ma.auto_field()
    title = ma.auto_field()
    description = ma.auto_field()
    completed = ma.auto_field()

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)

# Create a new Todo item
@app.route('/todos', methods=['POST'])
def add_todo():
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        completed = data.get('completed', False)

        if not title:
            return jsonify({"error": "Title is required"}), 400

        new_todo = Todo(title, description, completed)
        db.session.add(new_todo)
        db.session.commit()

        logging.info("Todo created successfully")
        return todo_schema.jsonify(new_todo), 201
    except Exception as e:
        logging.error(f"Error creating todo: {str(e)}")
        return jsonify({"error": "Failed to create todo"}), 500

# Retrieve all Todo items
@app.route('/todos', methods=['GET'])
def get_todos():
    try:
        all_todos = Todo.query.all()
        return todos_schema.jsonify(all_todos)
    except Exception as e:
        logging.error(f"Error fetching todos: {str(e)}")
        return jsonify({"error": "Failed to retrieve todos"}), 500

# Retrieve a single Todo item
@app.route('/todos/<int:id>', methods=['GET'])
def get_todo(id):
    todo = Todo.query.get(id)
    if not todo:
        return jsonify({"error": "Todo not found"}), 404
    return todo_schema.jsonify(todo)

# Update a Todo item
@app.route('/todos/<int:id>', methods=['PUT'])
def update_todo(id):
    try:
        todo = Todo.query.get(id)
        if not todo:
            return jsonify({"error": "Todo not found"}), 404

        data = request.get_json()
        todo.title = data.get('title', todo.title)
        todo.description = data.get('description', todo.description)
        todo.completed = data.get('completed', todo.completed)

        db.session.commit()
        logging.info("Todo updated successfully")
        return todo_schema.jsonify(todo)
    except Exception as e:
        logging.error(f"Error updating todo: {str(e)}")
        return jsonify({"error": "Failed to update todo"}), 500

# Delete a Todo item
@app.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    try:
        todo = Todo.query.get(id)
        if not todo:
            return jsonify({"error": "Todo not found"}), 404

        db.session.delete(todo)
        db.session.commit()
        logging.info("Todo deleted successfully")
        return jsonify({"message": "Todo deleted successfully"})
    except Exception as e:
        logging.error(f"Error deleting todo: {str(e)}")
        return jsonify({"error": "Failed to delete todo"}), 500

# Run the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
