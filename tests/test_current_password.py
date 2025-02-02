import pytest
from main import create_app, db as database
from model import User  # Corrected import path

@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    with app.app_context():
        database.create_all()
        yield app
        database.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='module')
def db(app):
    return database

def test_current_password(client, db):
    # Ensure clean state
    db.session.rollback()

    # Add a test user
    user = User(
        name="Test User",
        email="test@example.com",
        phone_number="1234567890",
        role="Customer",
        password="dummy"  # Temporary value
    )
    user.set_password("CurrentPass123")
    db.session.add(user)
    

    # Simulate login
    with client.session_transaction() as session:
        session['user_id'] = user.user_id

    # Test invalid current password
    response = client.post('/change-password', data={
        'currentPassword': 'WrongPass123',
        'newPassword': 'NewPass@123',
        'confirmPassword': 'NewPass@123'
    })
    

    # Test valid current password
    response = client.post('/change-password', data={
        'currentPassword': 'CurrentPass123',
        'newPassword': 'NewPass@123',
        'confirmPassword': 'NewPass@123'
    })
    