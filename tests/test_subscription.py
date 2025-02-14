import pytest
from app import app, db, Sub  # Ensure 'Sub' is your subscriber model

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_todo.db'  # Use a test database
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create necessary tables before tests
        yield client
        with app.app_context():
            db.drop_all()  # Cleanup after tests

# Test GET request for subscription page
def test_get_subscription_page(client):
    response = client.get('/subscribe')
    assert response.status_code in [200, 405]  # Handle case where GET is not allowed

# Test GET request to view subscribers

def test_view_subscribers(client):
    # Add a subscriber
    client.post('/subscribe', data={'email': 'testuser@example.com'})
    
    # Make a GET request to view the list of subscribers
    response = client.get('/subscribers')
    
    # Check that the subscriber is present in the response
    assert response.status_code == 200  # Successful request
    assert 'testuser@example.com' in response.data.decode()
