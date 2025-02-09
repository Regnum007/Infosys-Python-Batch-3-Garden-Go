# test_changepassword.py
from model import User,db


def test_change_password_valid(client):
    # Set up a test user
    with client.application.app_context():
        user = User(name="Test User", email="test@example.com", phone_number="1234567890", password="password", role="Customer")
        db.session.add(user)
        db.session.commit()  # Commit the user to the database

    # Make a POST request to change the password
    response = client.post('/change_password', data={
        'currentPassword': 'password',
        'newPassword': 'newpassword',
        'confirmPassword': 'newpassword'
    })

   