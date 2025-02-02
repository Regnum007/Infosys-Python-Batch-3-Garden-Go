# test_add_address.py

import pytest
from model import db, User, Address

@pytest.fixture
def app():
    from flask import Flask

    # Initialize Flask app for testing
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.secret_key = 'test_secret_key'

    # Initialize db with app
    db.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()

    yield app  # Yield app for testing

    # Clean up after tests
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    # Return Flask test client
    return app.test_client()


@pytest.fixture
def test_user(client):
    # Create a test user for the tests
    with client.application.app_context():
        user = User(name="Test User", email="test@example.com", phone_number="1234567890", password="password", role="Customer")
        db.session.add(user)
        db.session.commit()
        return user


def test_add_address_valid(client, test_user):
    # Test case: Add a valid address for a user
    response = client.post('/add_address', data={
        'street': '123 Main St',
        'city': 'Springfield',
        'state': 'IL',
        'postal_code': '62701'
    })

    


def test_add_address_missing_field(client, test_user):
    # Test case: Add address with missing fields
    response = client.post('/add_address', data={
        'street': '123 Main St',
        'city': 'Springfield',
        'state': 'IL'
        # Missing postal_code
    })

    # Verify that the request fails with the proper error message
    


def test_add_address_user_not_found(client):
    # Test case: Add address when the user does not exist
    response = client.post('/add_address', data={
        'user_id': 999,  # Non-existing user ID
        'street': '456 Elm St',
        'city': 'Shelbyville',
        'state': 'IN',
        'postal_code': '46501'
    })

   
