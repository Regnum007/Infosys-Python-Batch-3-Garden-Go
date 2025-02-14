import datetime
import pytest
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

# Setup Flask and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Example model
class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)  # Storing date as string for simplicity

# Sample route to render order data
@app.route('/orders/overview', methods=['GET'])
def get_orders_overview():
    today = datetime.date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    # Calculate total orders, today's orders, this month's orders, this year's orders
    total_orders = Order.query.count()
    orders_today = Order.query.filter(Order.date == str(today)).count()
    orders_this_month = Order.query.filter(Order.date >= str(month_start)).count()
    orders_this_year = Order.query.filter(Order.date >= str(year_start)).count()

    return jsonify({
        'total_orders': total_orders,
        'today': orders_today,
        'this_month': orders_this_month,
        'this_year': orders_this_year
    })

# Test case for all orders overview (total, today, this month, this year)
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create tables before each test

            # Sample data for testing
            today = datetime.date.today()
            month_start = today.replace(day=1)
            year_start = today.replace(month=1, day=1)
            
            # Add orders with different dates for variety in testing
            db.session.add(Order(status="dispatched", date=str(today)))  # Today's order
            db.session.add(Order(status="delivered", date=str(today)))  # Today's order
            db.session.add(Order(status="dispatched", date=str(month_start)))  # This month, but not today
            db.session.add(Order(status="delivered", date=str(month_start)))  # This month, but not today
            db.session.add(Order(status="in_transit", date=str(year_start)))  # This year, but not this month
            db.session.add(Order(status="failed_attempt", date=str(year_start)))  # This year, but not this month
            db.session.commit()
            
            yield client
        db.drop_all()  # Cleanup after test

def test_orders_overview(client):
    """Test that the orders overview correctly returns the counts for total, today, this month, and this year."""
    response = client.get('/orders/overview')
    data = response.get_json()

    today = datetime.date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    # Fetch orders for today, this month, and this year for dynamic comparison
    total_orders = Order.query.count()
    orders_today = Order.query.filter(Order.date == str(today)).count()
    orders_this_month = Order.query.filter(Order.date >= str(month_start)).count()
    orders_this_year = Order.query.filter(Order.date >= str(year_start)).count()

    # Assert the response matches the actual counts from the database
    assert data['total_orders'] == total_orders
    assert data['today'] == orders_today
    assert data['this_month'] == orders_this_month
    assert data['this_year'] == orders_this_year

    assert response.status_code == 200