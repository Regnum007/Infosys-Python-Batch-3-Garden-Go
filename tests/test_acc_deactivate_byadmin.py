import pytest
from main import create_app, db
from model import User
from flask.testing import FlaskClient

# Set up the Flask test client
@pytest.fixture
def client(app):
    return app.test_client()

# Fixture for creating and saving a user
@pytest.fixture
def user(app):
    user = User(name="Test User", email="testuser@example.com", password="testpassword", phone_number="1234567890")
    db.session.add(user)
    db.session.flush()
    db.session.commit()  # Commit to the database so that an `id` is generated
    
    return user



   

def test_deactivate_user_not_found(client: FlaskClient):
    # Send a POST request with a non-existent user ID
    response = client.post('/admin/deactivate/9999999')  # Assuming this user doesn't exist
    
def test_deactivate_user_invalid_id(client: FlaskClient):
    # Send a POST request with an invalid user ID (e.g., string instead of integer)
    response = client.post('/admin/deactivate/invalid_id')  # Invalid ID
  
