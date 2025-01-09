from flask import Flask, session
from models import Address, User
from __init__ import create_app, db
import pytest

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create all tables
        yield client
        with app.app_context():
            db.drop_all()  # Clean up after test

def test_view_addresses(client):
    # Register and login the user
    client.post('/signup', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'mobile': '1234567890',
        'password': 'password',
        'role': 'Customer'
    })
    client.post('/login', data={'email': 'test@example.com', 'password': 'password'})
    
    # Add some addresses manually
    client.post('/add-address', data={
        'street_address': '123 Main St',
        'locality': 'Locality 1',
        'city': 'City 1',
        'state': 'State 1',
        'postal_code': '12345'
    })
    
    client.post('/add-address', data={
        'street_address': '456 Another St',
        'locality': 'Locality 2',
        'city': 'City 2',
        'state': 'State 2',
        'postal_code': '67890'
    })

    # Test view addresses
    response = client.get('/address')

def test_add_address_invalid(client):
    # Register and login the user
    client.post('/signup', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'mobile': '1234567890',
        'password': 'password',
        'role': 'Customer'
    })
    client.post('/login', data={'email': 'test@example.com', 'password': 'password'})
    
    # Test adding an address with missing required fields (e.g., street_address)
    response = client.post('/add-address', data={
        'street_address': '',
        'locality': 'Invalid Locality',
        'city': 'Invalid City',
        'state': 'Invalid State',
        'postal_code': '00000'
    })
   
