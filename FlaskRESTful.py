import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite') # To Create db in the basedir
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)


# Create Model
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
   
# Schema   
class TodoSchema(ma.Schema):
   class Meta:
      model = Todo
      fields = ('id', 'title', 'description', 'completed')
      
# init schema
todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)


class TodoListView(Resource):
   def get(self):
      try:
         page = request.args.get('page', 1, type=int)
         per_page = request.args.get('per_page', 10, type=int)

         # Query todos and apply pagination
         pagination = Todo.query.paginate(page=page, per_page=per_page, error_out=False)
         
         todos = todos_schema.dump(pagination.items)
         
         response = {
               "todos": todos,
               "meta": {
                  "page": pagination.page,
                  "per_page": pagination.per_page,
                  "total": pagination.total,
                  "pages": pagination.pages,
               }
         }
         return jsonify(response)
         
         # Default Get: /todos == /todos?page=1&per_page=10
         # Get: /todos?page=1&per_page=15
         
      except Exception as e:
         return jsonify({"error": str(e)})

   def post(self):
      try:
         title = request.json.get('title')
         description = request.json.get('description')
         completed = request.json.get('completed', False)
         
         if not title:
            return jsonify({'error': 'Validation errors Title Required'})         
         new_todo = Todo(title=title, description=description, completed=completed)
      
         # Add new todo to the db
         db.session.add(new_todo)
         db.session.commit()

         return todo_schema.jsonify(new_todo)
   
      except Exception as e:
         db.session.rollback()
         return jsonify({'error': str(e)})
      
class TodoDetailView(Resource):
   def get(self, id):
      todo = Todo.query.get_or_404(id)
      # todo = db.session.get(Todo, id) # Query.get() method replaced with Session.get(). this will remove the warning that occurs during testing
      return todo_schema.jsonify(todo)
      
   def put(self, id):
      todo = Todo.query.get_or_404(id)
      todo.title = request.json.get('title', todo.title)
      todo.description = request.json.get('description', todo.description)
      todo.completed = request.json.get('completed', todo.completed)     
      
      try:
        db.session.commit()
        return todo_schema.jsonify(todo)
      except Exception as e:
         db.session.rollback()
         return jsonify({'Error': str(e)}), 400
         
   def delete(self, id):
      todo = Todo.query.get_or_404(id)
      
      db.session.delete(todo)
      db.session.commit()
      
      return jsonify({"Message": "Successfully Deleted"})


# Routes
api.add_resource(TodoListView, '/todos')   
api.add_resource(TodoDetailView, '/todos/<int:id>')   


if __name__ == '__main__':
   with app.app_context():
      db.create_all()
   app.run(debug=True)
