import pytest
from main import create_app, db
from model import User
from flask.testing import FlaskClient

# Set up the Flask test client
@pytest.fixture
def client(app):
    return app.test_client()

# Fixture for creating and saving a user with reactivation request
@pytest.fixture
def user_with_reactivation_request(app):
    # Create the user object with reactivation request
    user = User(name="Test User", email="testuser@example.com", password="testpassword", phone_number="1234567890")
    
    db.session.add(user)  # Add user to the session
    db.session.commit()  # Commit to save user
    
    
    return user


   
def test_approve_reactivation_request_not_found(client: FlaskClient):
    # Send a POST request with a non-existent user ID to approve the reactivation request
    response = client.post('/admin/approve-request/9999999')  # Assuming this user doesn't exist
    

def test_reject_reactivation_request_not_found(client: FlaskClient):
    # Send a POST request with a non-existent user ID to reject the reactivation request
    response = client.post('/admin/reject-request/9999999')  # Assuming this user doesn't exist


def test_invalid_user_id_approve(client: FlaskClient):
    # Send a POST request with an invalid user ID (e.g., string instead of integer) to approve reactivation
    response = client.post('/admin/approve-request/invalid_id')  # Invalid ID

def test_invalid_user_id_reject(client: FlaskClient):
    # Send a POST request with an invalid user ID (e.g., string instead of integer) to reject reactivation
    response = client.post('/admin/reject-request/invalid_id')  # Invalid ID
    