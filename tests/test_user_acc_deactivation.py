import pytest
from main import create_app
from model import db, User  # Import db from the model to interact with the database
from flask import Flask

# Set up the test environment for the app
@pytest.fixture(scope='module')
def app():
    app = create_app()  # Use the app factory to create an app instance
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory database for testing
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking for testing
    app.secret_key = 'test_secret_key'

    # Do NOT call db.init_app(app) again because it's already done in the main.py
    # db.init_app(app)  # Remove this line

    with app.app_context():
        db.create_all()  # Create the test database tables

    yield app  # Return the app instance to the tests

    with app.app_context():
        db.drop_all()  # Clean up the test database after tests are done

# Fixture to create a user for testing purposes
@pytest.fixture
def registered_user(app):
    # Create a registered user for testing
    user = User(name="Test User", email="testuser@example.com", password="testpassword", phone_number="1234567890")
    db.session.add(user)

    return user

# Example test for account deactivation
def test_deactivation_request(app, registered_user):
    with app.test_client() as client:
        response = client.post('/deactivate', json={'email': registered_user.email, 'password': 'testpassword'})
        
# Example test for invalid password
def test_deactivation_request_invalid_password(app, registered_user):
    with app.test_client() as client:
        response = client.post('/deactivate', json={'email': registered_user.email, 'password': 'wrongpassword'})
       
