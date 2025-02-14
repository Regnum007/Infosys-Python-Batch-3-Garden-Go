import pytest
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

# Setup Flask and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Example model
class Courier(db.Model):
    __tablename__ = 'couriers'
    courier_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)

# Sample route to render courier data
@app.route('/courier_data', methods=['GET'])
def get_courier_data():
    couriers = Courier.query.all()  # Fetch all courier records from the database
    courier_list = [
        {"courier_id": courier.courier_id, "order_id": courier.order_id, 
         "name": courier.name, "status": courier.status, "date": courier.date}
        for courier in couriers
    ]
    return jsonify(courier_list)

# Test case for empty database
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():  # Ensure app context is pushed
            db.create_all()  # Create tables if not exist
            yield client
        db.drop_all()  # Cleanup after the test

def test_empty_database(client):
    """Test that the /courier_data route returns an empty list when no data exists."""
    response = client.get('/courier_data')
    data = response.get_json()
    
    # Assert that the response contains an empty list
    assert data == []
    assert response.status_code == 200
