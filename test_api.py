import pytest
from FlaskRESTful import app, db, Todo

@pytest.fixture
def client():
   """Set up the Flask test client and a fresh database for each test."""
   
   app.config['TESTING'] = True
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

   with app.test_client() as client:
      with app.app_context():
            db.create_all() 
      
      yield client
      
      with app.app_context():
            db.drop_all()  

def test_get_empty_todos(client):
   """Test GET /todos when no todos exist."""
   
   response = client.get('/todos')
   
   assert response.status_code == 200
   data = response.get_json()
   assert data['todos'] == []  # No todos exist


def test_post_todo(client):
   """Test POST /todos to create a new todo."""
   
   response = client.post('/todos', 
   json={
      'title': 'Test Todo',
      'description': 'This is a test todo.',
      'completed': False
   })
   
   assert response.status_code == 200
   data = response.get_json()
   assert data['title'] == 'Test Todo'
   assert data['description'] == 'This is a test todo.'
   assert data['completed'] is False

def test_get_todo_by_id(client):
   """Test GET /todos/<id>."""
   
   todo = Todo(title='Test Todo', description='Test Description', completed=False)
   
   with app.app_context():
      db.session.add(todo)
      db.session.commit()
      todo_id = todo.id  # Store the ID before leaving the session
   
   response = client.get(f'/todos/{todo_id}')
   
   assert response.status_code == 200
   data = response.get_json()
   assert data['title'] == 'Test Todo'
   assert data['description'] == 'Test Description'
   assert data['completed'] is False


def test_put_todo(client):
   """Test PUT /todos/<id> to update a todo."""
   
   todo = Todo(title='Old Title', description='Old Description', completed=False)
   
   with app.app_context():
      db.session.add(todo)
      db.session.commit()
      todo_id = todo.id
   
   # Update the todo
   response = client.put(f'/todos/{todo_id}', 
   json={
      'title': 'New Title',
      'description': 'New Description',
      'completed': True
   })
   
   
   assert response.status_code == 200
   data = response.get_json()
   assert data['title'] == 'New Title'
   assert data['description'] == 'New Description'
   assert data['completed'] is True


def test_delete_todo(client):
   """Test DELETE /todos/<id> to remove a todo."""
   
   todo = Todo(title='Test Todo', description='Test Description', completed=False)
   
   with app.app_context():
      db.session.add(todo)
      db.session.commit()
      todo_id = todo.id

   response = client.delete(f'/todos/{todo_id}')
   
   assert response.status_code == 200
   data = response.get_json()
   assert data['Message'] == 'Successfully Deleted'

   # # Verify deletion
   # with app.app_context():
   #    assert Todo.query.get(todo_id) is None
