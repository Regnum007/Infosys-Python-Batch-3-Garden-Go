import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Setup Flask and SQLAlchemy for testing
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True
db = SQLAlchemy(app)

# Define the Order model
class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    courier_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    status_percentage = db.Column(db.Integer, nullable=False)

# Setup Flask route for tracking orders
@app.route('/track/<int:order_id>', methods=['GET'])
def track_order(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    if order:
        return {
            'order_id': order.order_id,
            'courier_name': order.courier_name,
            'status': order.status,
            'status_percentage': order.status_percentage
        }, 200
    return {'error': 'Order not found'}, 404

# Pytest fixture to initialize the test client and database
@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create tables

            # Add sample data
            orders = [
                Order(order_id=1, courier_name="Alex Taylor", status="Dispatched", status_percentage=25),
                Order(order_id=2, courier_name="Taylor Swift", status="In Transit", status_percentage=50),
                Order(order_id=3, courier_name="John Doe", status="Delivered", status_percentage=100),
            ]
            db.session.bulk_save_objects(orders)
            db.session.commit()

        yield client
        with app.app_context():
            db.drop_all()  # Cleanup after test

# Test case for tracking orders
def test_track_order(client):
    """Test if the correct order is retrieved by ID."""
    
    # Case 1: Valid order ID
    response = client.get('/track/1')  # Query order with ID 1
    data = response.get_json()

    assert response.status_code == 200
    assert data['order_id'] == 1
    assert data['courier_name'] == "Alex Taylor"
    assert data['status'] == "Dispatched"
    assert data['status_percentage'] == 25

    # Case 2: Invalid order ID
    response = client.get('/track/99')  # Query non-existent order
    data = response.get_json()

    assert response.status_code == 404
    assert data['error'] == "Order not found"
