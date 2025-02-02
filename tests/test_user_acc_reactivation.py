import pytest
from main import create_app, db  # Import the app and db instance from your main module
from model import User  # Assuming the model is in this location

@pytest.fixture(scope='module')
def app():
    app = create_app()  # Create the Flask app using the factory method
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory SQLite database for testing
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.create_all()  # Create the database tables for the test
    yield app
    with app.app_context():
        db.drop_all()  # Drop the tables after tests are done

@pytest.fixture
def registered_user(app):
    # Create a user in the database with `is_active=False`
    phone_number = "123456789"  # Make sure this is unique for testing
    user = User(name="Test User", email="testuser@example.com", password="testpassword", phone_number=phone_number, )
    db.session.add(user)
    db.session.commit()  # Commit to save the user to the database
    return user

def test_user_account_reactivation(app, registered_user):
    # Simulate the reactivation of the user's account
    registered_user.is_active = True  # Reactivate the account
    db.session.commit()  # Commit the change to the database

    # Retrieve the user from the database and check if `is_active` is now True
    user = User.query.filter_by(email="testuser@example.com").first()
    
def test_user_account_reactivation_invalid_user(app):
    # Try to reactivate a non-existent user
    user = User.query.filter_by(email="nonexistent@example.com").first()
    