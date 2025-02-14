from flask.testing import FlaskClient
import pytest
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from integration.model import Order, OrderDetail, db, User, Category, Product 

# Initialize the app and create the database
@pytest.fixture
def init_db():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app) 

    with app.app_context():
        db.create_all() 
        seed_data()

        yield db 

        db.session.remove() 
        db.drop_all() 

@pytest.fixture
def test_client(init_db):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register a route for creating a user (replace with your actual route)
    @app.route('/users', methods=['POST'])
    def create_user():
        data = request.get_json()
        try:
            new_user = User(
                name=data['name'],
                email=data['email'],
                phone_number=data['phone_number'],
                password=generate_password_hash(data['password'])
            )
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'message': 'User created successfully'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    with app.app_context():
        db.create_all()
        yield app.test_client()

        db.session.remove()
        db.drop_all()

# Seed the database with some sample data
def seed_data():
    # Create a test user
    user = User(name="Test User", email="testuser@example.com", phone_number=1234567890, password=generate_password_hash("password123"))
    db.session.add(user)

    # Create a test product
    product = Product(name="Yarrow", cost_price=15.0, weight=0.1) 
    db.session.add(product)

    # Create a test category
    category = Category(name="Herbs", description="All medicinal herbs")
    db.session.add(category)

    # Commit the changes to the database
    db.session.commit()

def test_create_user(init_db):
    """Test user creation."""
    user = User.query.filter_by(email="testuser@example.com").first()
    assert user is not None
    assert user.name == "Test User"
    assert user.email == "testuser@example.com"

def test_product_seeding(init_db):
    """Test that products are seeded correctly."""
    product_count = Product.query.count()
    assert product_count > 0 

    # Check if a particular product exists
    product = Product.query.filter_by(name="Yarrow").first()
    assert product is not None
    assert product.name == "Yarrow"
    assert product.cost_price == 15.0
    assert product.weight == 0.1

def test_create_order(init_db):
    """Test order creation."""
    user = User.query.first() 
    product = Product.query.first() 

    order = Order(user_id=user.user_id, total_price=100.0, shipping_cost=10.0, status="Pending",prices=30.0 )
    db.session.add(order)
    db.session.commit()

    order_detail = OrderDetail(order_id=order.order_id, product_id=product.product_id, quantity=2, sub_Total=30.0)
    db.session.add(order_detail)
    db.session.commit()

    # Verify order is in the database
    order = Order.query.filter_by(user_id=user.user_id).first()
    assert order is not None
    assert order.status == "Pending"
    assert len(order.order_details) > 0

def test_create_category(init_db):
    """Test category creation."""
    category = Category(name="Herbs", description="All medicinal herbs")
    db.session.add(category)
    db.session.commit()

    # Verify category is in the database
    retrieved_category = Category.query.filter_by(name="Herbs").first()
    assert retrieved_category is not None
    assert retrieved_category.description == "All medicinal herbs"

def test_create_user_with_post(test_client):
    """Test creating a user with a POST request."""
    user_data = {
        "name": "New Test User",
        "email": "newtestuser@example.com",
        "phone_number": 9876543210,
        "password": "password456"
    }
    response = test_client.post('/users', json=user_data)
    assert response.status_code == 201
    assert response.json['message'] == 'User created successfully' 

    # Verify user is created in the database
    new_user = User.query.filter_by(email="newtestuser@example.com").first()
    assert new_user is not None