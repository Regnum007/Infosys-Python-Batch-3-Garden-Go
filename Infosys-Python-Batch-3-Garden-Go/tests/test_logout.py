import pytest
from flask import session
from main import create_app
from model import User,db

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

def test_logout(client):
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
    

    
    # Test logging out the user
    response = client.get('/logout')
    
    
