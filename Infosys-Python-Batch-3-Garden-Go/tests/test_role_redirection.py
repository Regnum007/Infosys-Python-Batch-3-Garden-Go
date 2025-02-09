import pytest
from main import create_app, db
from model import User  # Corrected import for User class
from flask import session



def test_login_get_request(client):
    """Test GET request to the login route."""
    response = client.get('/login')
    

def test_login_post_request_valid_admin(client):
    """Test POST request with valid admin credentials."""
    # Create a mock admin user
    user = User(
        name="Admin User",
        email="admin@example.com",
        phone_number="1234567890",
        password="adminpass",
        role="Admin"
    )
    user.set_password("adminpass")  # Ensure password is hashed
    

    response = client.post('/login', data={"email": "admin@example.com", "password": "adminpass"})
    
def test_login_post_request_invalid_password(client):
    """Test POST request with invalid password."""
    # Create a mock customer user
    user = User(
        name="Customer User",
        email="user@example.com",
        phone_number="1234567890",
        password="userpass",
        role="Customer"
    )
    user.set_password("userpass")
    with create_app().app_context():
        db.session.add(user)
       
    response = client.post('/login', data={"email": "user@example.com", "password": "wrongpass"})
    
def test_login_post_request_email_not_exist(client):
    """Test POST request with non-existent email."""
    response = client.post('/login', data={"email": "nonexistent@example.com", "password": "testpass"})
    