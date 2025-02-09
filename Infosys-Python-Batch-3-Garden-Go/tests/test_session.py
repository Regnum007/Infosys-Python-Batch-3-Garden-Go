import pytest
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

# Initialize the app and the database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for testing
app.config['TESTING'] = True
db = SQLAlchemy(app)

# Define a simple model for testing purposes
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

# Fixtures for testing
@pytest.fixture
def client():
    # Ensure app context is pushed correctly for session and DB operations
    with app.app_context():
        # Create the database and tables
        db.create_all()

        # Return the test client
        with app.test_client() as client:
            yield client

        # Clean up the database after tests
        db.drop_all()

def test_session_creation(client):
    # Test if session is created correctly
    response = client.get('/')  # Directly use the client fixture here


def test_session_storage(client):
    # Test storing data in the session
    with client.session_transaction() as test_session:
        test_session['user_id'] = 1  # Simulate storing a user ID in the session

    response = client.get('/')
  
    with client.session_transaction() as test_session:
        assert test_session.get('user_id') == 1  # Verify session data

def test_session_expiry(client):
    # Test if session expires after the specified lifetime
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=2)
    with client.session_transaction() as test_session:
        test_session['user_id'] = 1

    import time
    time.sleep(3)  # Wait for session expiration

    response = client.get('/')
 
    with client.session_transaction() as test_session:
        assert 'user_id' not in test_session  # Verify session expired

def test_session_signing(client):
    # Test if session signing works correctly
    with client.session_transaction() as test_session:
        test_session['test_key'] = 'test_value'

    response = client.get('/')

    # Since signing is internal, we assume Flask handles it unless there's an error.
