from flask import Flask
from werkzeug.security import generate_password_hash
from model import db, User, PasswordResetToken



def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
    app.secret_key = 'test_secret_key'
    app.config['MAIL_SUPPRESS_SEND'] = True  # Suppress actual email sending in test

    # Create the database tables
    with app.app_context():
        db.create_all()

    # Initialize the test client
    with app.test_client() as client:
        yield client

    # Cleanup after test
    with app.app_context():
        db.drop_all()

# Test case: Request password reset with registered email
def test_request_reset_valid_email(client):
    # Create a test user with a valid email
    with client.application.app_context():
        user = User(name="Test User", email="test@example.com", phone_number="1234567890", password=generate_password_hash("password"), role="Customer")
        db.session.add(user)
        db.session.commit()

    # Simulate the POST request to request a password reset
    response = client.post('/request-reset', data={'email': 'test@example.com'})

       

# Test case: Request password reset with unregistered email
def test_request_reset_unregistered_email(client):
    # Simulate the POST request to request a password reset with an unregistered email
    response = client.post('/request-reset', data={'email': 'nonexistent@example.com'})


# Test case: Request password reset with empty email
def test_request_reset_empty_email(client):
    # Simulate the POST request with an empty email
    response = client.post('/request-reset', data={'email': ''})


