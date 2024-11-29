# class-based view using Flask's MethodView

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask.views import MethodView

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite') # To Create db in the basedir
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)

class Todo(db.Model):
   id = db.Column(db.Integer, primary_key=True) 
   title = db.Column(db.String(100), nullable=False)
   description = db.Column(db.String(255), nullable=True)
   completed = db.Column(db.Boolean, default=False)
   
   def __init__(self, title, description, completed):
      self.title = title
      self.description = description
      self.completed = completed
      
   def __repr__(self):
      return f'<Todo: {self.title}>'
   
   
class TodoSchema(ma.Schema):
   class Meta:
      fields = ('id', 'title', 'description', 'completed')
      
      
# init schema
todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)

class TodoView(MethodView):
   def get(self, id=None):
      if id is None:
         # Get All Todos
         todos = Todo.query.all()
         return todos_schema.jsonify(todos)
      else:
         # Get Single todo
         todo = Todo.query.get(id)
         if todo:
            return todo_schema.jsonify(todo)
         else:
            return jsonify({'Error':'Resource not found'}), 404 # Resource not found
         
   def post(self):
      try:
         title = request.json.get('title')
         description = request.json.get('description')
         completed = request.json.get('completed', False)
         
         if not title:
            return jsonify({'error': 'Validation errors'}), 400
         
         new_todo = Todo(title=title, description=description, completed=completed)
         
         # Add new todo to the db
         db.session.add(new_todo)
         db.session.commit()

         return todo_schema.jsonify(new_todo), 201
      
      except Exception as e:
         db.session.rollback()
         return jsonify({'error': str(e)}), 500
      
      
   def put(self, id):
      try:
         todo = Todo.query.get(id)
         todo.title = request.json.get('title', todo.title)
         todo.description = request.json.get('description', todo.description)
         todo.completed = request.json.get('completed', todo.completed)
               
         db.session.commit()

         return todo_schema.jsonify(todo)
      except Exception as e:
         db.session.rollback()
         return jsonify({'error': str(e)}), 500
      
   def delete(self, id):
      todo = Todo.query.get(id)
      if todo is None:
         return jsonify({"Error": "Todo not found"})
      db.session.delete(todo)
      db.session.commit()
      
      return jsonify({"Message": "Successfully Deleted"})
      
# Register the MethodView class with routes
todo_view = TodoView.as_view('todo_view')
app.add_url_rule('/todos', view_func=todo_view, methods=['GET', 'POST'])
app.add_url_rule('/todos/<int:id>', view_func=todo_view, methods=['GET', 'PUT', 'DELETE'])

if __name__ == '__main__':
   with app.app_context():
      db.create_all()
   app.run(debug=True)