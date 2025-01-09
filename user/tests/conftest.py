import pytest
from __init__ import create_app, db  # Import your `create_app` function and `db` object

@pytest.fixture
def app():
    # Create a test instance of the app
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Use in-memory database for testing
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing purposes
    })

    # Create the database schema
    with app.app_context():
        db.create_all()

    yield app  # Provide the app instance to the test

    # Cleanup the database after tests
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    # Provide a test client to the test
    return app.test_client()

@pytest.fixture
def runner(app):
    # Provide a CLI runner to the test
    return app.test_cli_runner()
