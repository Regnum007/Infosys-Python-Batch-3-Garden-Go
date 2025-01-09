from models import db, User
def test_login(client):
    # Create a test user in the database
    from models import User
    with client.application.app_context():
        user = User(name="Test User", email="test@example.com", phone_number="1234567890", password="password", role="Customer")
        db.session.add(user)
        db.session.commit()

    # Valid login
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password',
    })
   

    # Invalid login
    response = client.post('/login', data={
        'email': 'wrong@example.com',
        'password': 'password',
    })