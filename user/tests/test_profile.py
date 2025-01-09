import pytest
from flask import session
from models import User
from __init__ import create_app, db

def client():
    # Setup the Flask test client and in-memory database for testing
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory database
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create all tables
        yield client
        with app.app_context():
            db.drop_all()  # Clean up after test

def test_profile_page_logged_in(client):
    # Register a new user
    client.post('/signup', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'mobile': '1234567890',
        'password': 'password',
        'role': 'Customer'
    })
    
    # Login the user
    client.post('/login', data={'email': 'test@example.com', 'password': 'password'})
    
  
    
    # Test accessing the profile page
    response = client.get('/profile')
  
def test_profile_page_not_logged_in(client):
    # Test accessing the profile page without being logged in
    response = client.get('/profile')
 
