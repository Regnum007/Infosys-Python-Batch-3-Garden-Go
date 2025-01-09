from models import db, User
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
    app.secret_key = 'test_secret_key'

    # Create the database tables
    with app.app_context():
        db.create_all()

    # Initialize the test client
    with app.test_client() as client:
        yield client

    # Cleanup after test
    with app.app_context():
        db.drop_all()

# Test case: Valid password change
def test_change_password_valid(client):
    # Create a test user
    with client.application.app_context():
        user = User(name="Test User", email="test@example.com", phone_number="1234567890", password="password", role="Customer")
        db.session.add(user)
        db.session.commit()


    # Change password
    response = client.post('/change_password', data={
        'currentPassword': 'password',
        'newPassword': 'newpassword',
        'confirmPassword': 'newpassword'
    })

  
   

# Test case: Invalid current password
def test_change_password_invalid_current_password(client):
    # Create a test user
    with client.application.app_context():
        user = User(name="Test User", email="test@example.com", phone_number="1234567890", password="password", role="Customer")
        db.session.add(user)
        db.session.commit()

  

    # Attempt to change password with incorrect current password
    response = client.post('/change_password', data={
        'currentPassword': 'wrongpassword',
        'newPassword': 'newpassword',
        'confirmPassword': 'newpassword'
    })

   

# Test case: New password and confirm password do not match
def test_change_password_mismatch(client):
    # Create a test user
    with client.application.app_context():
        user = User(name="Test User", email="test@example.com", phone_number="1234567890", password="password", role="Customer")
        db.session.add(user)
        db.session.commit()

 

    # Attempt to change password with mismatched new and confirm passwords
    response = client.post('/change_password', data={
        'currentPassword': 'password',
        'newPassword': 'newpassword',
        'confirmPassword': 'differentpassword'
    })



# Test case: User not logged in
def test_change_password_not_logged_in(client):
    # Simulate not logged in (no user_id in session)
    response = client.post('/change_password', data={
        'currentPassword': 'password',
        'newPassword': 'newpassword',
        'confirmPassword': 'newpassword'
    })
