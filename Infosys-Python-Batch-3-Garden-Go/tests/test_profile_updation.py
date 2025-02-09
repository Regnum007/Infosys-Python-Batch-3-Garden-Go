from sqlite3 import IntegrityError
import pytest
from flask import session
from model import User
from main import create_app, db
from sqlalchemy.exc import IntegrityError

@pytest.fixture(scope='module')
def app():
    """Set up the Flask app in testing mode."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use an in-memory SQLite database
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test_secret_key",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='module')
def client(app):
    """Set up a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='module')
def create_test_user():
    """Create a test user in the database."""
    user = User(
        name="Test User",
        email="test@example.com",
        phone_number="1234567890",
        role="Customer",
        password="TestPassword@123"  # Provide the required password argument
    )
    db.session.add(user)
    db.session.commit()
    return user




def test_profile_update_success(client, create_test_user):
    """Test successful profile update."""
    user = create_test_user

    # Simulate login
    with client.session_transaction() as session:
        session['user_id'] = user.user_id

    # Perform the update
    response = client.post('/profile', data={
        'name': 'Updated Test User',
        'email': 'updated@example.com',
        'mobile': '0987654321'
    }, follow_redirects=True)


  


def test_profile_update_invalid_name(client, create_test_user):
    """Test profile update with an invalid name."""
    user = create_test_user

    # Simulate login
    with client.session_transaction() as session:
        session['user_id'] = user.user_id

    # Perform the update with an invalid name
    response = client.post('/profile', data={
        'name': '123InvalidName!',
        'email': 'updated@example.com',
        'mobile': '0987654321'
    }, follow_redirects=True)

  


def test_profile_update_invalid_email(client, create_test_user):
    """Test profile update with an invalid email."""
    user = create_test_user

    # Simulate login
    with client.session_transaction() as session:
        session['user_id'] = user.user_id

    # Perform the update with an invalid email
    response = client.post('/profile', data={
        'name': 'Updated Test User',
        'email': 'invalidemail',
        'mobile': '0987654321'
    }, follow_redirects=True)

  


def test_profile_update_invalid_phone(client, create_test_user):
    """Test profile update with an invalid phone number."""
    user = create_test_user

    # Simulate login
    with client.session_transaction() as session:
        session['user_id'] = user.user_id

    # Perform the update with an invalid phone number
    response = client.post('/profile', data={
        'name': 'Updated Test User',
        'email': 'updated@example.com',
        'mobile': '123'
    }, follow_redirects=True)



def test_profile_update_email_conflict(client, create_test_user):
    try:
        # Your test logic here...
        pass
    except Exception:
        db.session.rollback()
        raise  # Re-raise the exception for proper test reporting

