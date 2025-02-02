# conftest.py
import pytest
from flask import Flask
from model import db  # Import the db instance from your model file

@pytest.fixture
def app():
    # Create a new Flask app
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database
    app.secret_key = 'test_secret_key'

    # Initialize the SQLAlchemy instance with the app (you do not need to modify model.py)
    db.init_app(app)

    # Create the database tables
    with app.app_context():
        db.create_all()

    yield app  # Yield the app object for the test

    # Cleanup after tests
    with app.app_context():
        db.drop_all()

# Define the client fixture
@pytest.fixture
def client(app):
    return app.test_client()  # Return the test client for your app
