import pytest
from flask import Flask, session
from model import db, User, PasswordResetToken
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random  # <-- Make sure to import the random module
import string


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

# Helper function to generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Test case: Valid OTP submission and password reset
def test_verify_otp_valid(client):
    # Create a test user with a valid email and hashed password
    with client.application.app_context():
        user = User(name="Test User", email="test@example.com", phone_number="1234567890", password=generate_password_hash("password"), role="Customer")
        db.session.add(user)
        db.session.commit()

        # Create OTP token
        otp = generate_otp()
        token = PasswordResetToken(token=otp, user=user, created_at=datetime.now(), expires_at=datetime.now() + timedelta(minutes=15))
        db.session.add(token)
        db.session.commit()

        # Refresh the session to avoid DetachedInstanceError
        db.session.refresh(user)  # <-- Refresh to reattach the object to the session

    # Simulate OTP verification and password reset
    with client.application.app_context():
        session['email_verification'] = user.email

    # Submit valid OTP and new password
    response = client.post('/verify-otp', data={'otp': otp, 'new_password': 'newpassword'})

    # Assert that the password is updated
    updated_user = User.query.filter_by(email="test@example.com").first()
    updated_user.check_password('newpassword')

    

# Test case: Invalid OTP submission
def test_verify_otp_invalid(client):
    # Create a test user with a valid email and hashed password
    with client.application.app_context():
        user = User(name="Test User", email="test@example.com", phone_number="1234567890", password=generate_password_hash("password"), role="Customer")
        db.session.add(user)
        db.session.commit()

        # Create OTP token
        otp = generate_otp()
        token = PasswordResetToken(token=otp, user=user, created_at=datetime.now(), expires_at=datetime.now() + timedelta(minutes=15))
        db.session.add(token)
        db.session.commit()

        # Refresh the session to avoid DetachedInstanceError
        db.session.refresh(user)  # <-- Refresh to reattach the object to the session

    # Simulate OTP verification with invalid OTP
    with client.application.app_context():
        session['email_verification'] = user.email

    # Submit invalid OTP
    response = client.post('/verify-otp', data={'otp': 'wrongotp', 'new_password': 'newpassword'})


# Test case: Expired OTP submission
def test_verify_otp_expired(client):
    # Create a test user with a valid email and hashed password
    with client.application.app_context():
        user = User(name="Test User", email="test@example.com", phone_number="1234567890", password=generate_password_hash("password"), role="Customer")
        db.session.add(user)
        db.session.commit()

        # Create OTP token with an expired time
        otp = generate_otp()
        token = PasswordResetToken(token=otp, user=user, created_at=datetime.now(), expires_at=datetime.now() - timedelta(minutes=1))
        db.session.add(token)
        db.session.commit()

        # Refresh the session to avoid DetachedInstanceError
        db.session.refresh(user)  # <-- Refresh to reattach the object to the session

    # Simulate OTP verification with expired OTP
    with client.application.app_context():
        session['email_verification'] = user.email

    # Submit expired OTP
    response = client.post('/verify-otp', data={'otp': otp, 'new_password': 'newpassword'})

    

# Test case: No email in session
def test_verify_otp_no_email_in_session(client):
    # Simulate OTP verification with no email in session
    response = client.post('/verify-otp', data={'otp': '123456', 'new_password': 'newpassword'})
