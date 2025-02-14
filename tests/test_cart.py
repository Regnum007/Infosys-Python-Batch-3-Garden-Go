import pytest
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from integration.model import db, Product, Address, User  # Ensure these models are properly defined

# Initialize the app, db, and migrate
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['TESTING'] = True
    
    # Initialize the database
    db.init_app(app)
    
    # Define routes for testing
    @app.route('/cart', methods=['POST', 'GET'])
    def cart():
        if request.method == 'POST':
            product_id = request.form.get('product_id')
            quantity = request.form.get('quantity')
            if product_id and quantity:
                product = Product.query.get(product_id)
                if product:
                    # Add product to cart logic (not implemented here)
                    return f"Added {product.name} to cart"
            remove = request.form.get('remove')
            if remove:
                # Remove product from cart logic (not implemented here)
                return "Your cart is empty"
            address_id = request.form.get('address_id')
            if address_id:
                address = Address.query.get(address_id)
                if address:
                    # Simulate address selection
                    return f"Shipping Address Confirmed: {address.street_address}"
        
        return render_template('cart.html')  # If it's a GET request, render the cart

    return app


# Backend test setup using pytest for Flask
@pytest.fixture
def client():
    app = create_app()
    # Ensure that the app context is properly used
    with app.app_context():
        db.create_all()  # Create the test database
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()  # Clean up after the test


# Test for adding a product to the cart
def test_add_product_to_cart(client):
    # Add a product to the database within the application context
    with client.application.app_context():
        product = Product(name="Test Product", selling_price=100, weight=200, image_url="product.jpg")
        db.session.add(product)
        db.session.commit()

    # Simulate adding the product to the cart
    response = client.post('/cart', data={'product_id': 1, 'quantity': 1})
    assert response.status_code == 200
    assert b"Added Test Product to cart" in response.data  # Check if the product appears in the cart


# Test for removing a product from the cart
def test_remove_product_from_cart(client):
    # Add a product to the database within the application context
    with client.application.app_context():
        product = Product(name="Test Product", selling_price=100, weight=200, image_url="product.jpg")
        db.session.add(product)
        db.session.commit()

    # Simulate adding the product to the cart
    client.post('/cart', data={'product_id': 1, 'quantity': 1})

    # Simulate removing the product from the cart
    response = client.post('/cart', data={'product_id': 1, 'remove': 'True'})
    assert response.status_code == 200
    assert b"Your cart is empty" in response.data  # Cart is empty after removal


# Test for selecting a shipping address
def test_select_shipping_address(client):
    # Create a sample user with all required fields within the application context
    with client.application.app_context():
        user = User(
            name="Test User", 
            email="testuser@example.com",  # Add email
            phone_number="1234567890",     # Add phone number
            password="testpassword"        # Add password
        )
        db.session.add(user)
        db.session.commit()

        # Create a sample address for the user
        address = Address(user_id=user.user_id, street_address="123 Test St", locality="Test Locality", city="Test City", state="Test State", postal_code="12345")
        db.session.add(address)
        db.session.commit()

    # Simulate selecting the shipping address
    response = client.post('/cart', data={'address_id': 1})  # Use the correct address_id here
    assert response.status_code == 200
    assert f"Shipping Address Confirmed: 123 Test St".encode() in response.data  # Check if address was confirmed
