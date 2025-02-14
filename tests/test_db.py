from flask.testing import FlaskClient
import pytest
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from ..model import db, User, Category, Product


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app.test_client()

        db.session.remove()
        db.drop_all()

# CRUD Tests for User
def test_user_crud_operations(test_client):
    with test_client.application.app_context():
        # Create
        user = User(name="John Doe", email="john@example.com", phone_number=1234567890, password="password123")
        db.session.add(user)
        db.session.commit()

        assert user.user_id is not None

        # Read
        retrieved_user = User.query.filter_by(email="john@example.com").first()
        assert retrieved_user.name == "John Doe"

        # Update
        retrieved_user.name = "John Updated"
        db.session.commit()
        updated_user = User.query.filter_by(email="john@example.com").first()
        assert updated_user.name == "John Updated"

        # Delete
        db.session.delete(updated_user)
        db.session.commit()
        deleted_user = User.query.filter_by(email="john@example.com").first()
        assert deleted_user is None

# CRUD Tests for Category
def test_category_crud_operations(test_client):
    with test_client.application.app_context():
        # Create
        category = Category(name="Herbs", description="Medicinal plants")
        db.session.add(category)
        db.session.commit()

        assert category.category_id is not None

        # Read
        retrieved_category = Category.query.filter_by(name="Herbs").first()
        assert retrieved_category.description == "Medicinal plants"

        # Update
        retrieved_category.description = "Herbal plants"
        db.session.commit()
        updated_category = Category.query.filter_by(name="Herbs").first()
        assert updated_category.description == "Herbal plants"

        # Delete
        db.session.delete(updated_category)
        db.session.commit()
        deleted_category = Category.query.filter_by(name="Herbs").first()
        assert deleted_category is None

# CRUD Tests for Product
def test_product_crud_operations(test_client):
    with test_client.application.app_context():
        # Prerequisite: Create Category
        category = Category(name="Seeds", description="Various seeds")
        db.session.add(category)
        db.session.commit()

        # Create
        product = Product(name="Basil Seeds", description="Healthy seeds", category_id=category.category_id, 
                          cost_price=10.0, selling_price=15.0, weight=100, stock_quantity=50)
        db.session.add(product)
        db.session.commit()

        assert product.product_id is not None

        # Read
        retrieved_product = Product.query.filter_by(name="Basil Seeds").first()
        assert retrieved_product.description == "Healthy seeds"

        # Update
        retrieved_product.description = "Nutritious seeds"
        db.session.commit()
        updated_product = Product.query.filter_by(name="Basil Seeds").first()
        assert updated_product.description == "Nutritious seeds"

        # Delete
        db.session.delete(updated_product)
        db.session.commit()
        deleted_product = Product.query.filter_by(name="Basil Seeds").first()
        assert deleted_product is None
