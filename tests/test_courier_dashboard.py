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

# Test case for checking if data is rendered correctly
@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Ensure the app context is pushed before creating the test client
    with app.app_context():
        db.create_all()  # Create the tables
        with app.test_client() as client:
            yield client  # Provide the test client for the test
        db.drop_all()  # Cleanup after the test

def test_display_courier_data_dynamic(client):
    """Test that the /courier_data endpoint correctly renders data dynamically."""

    # Simulate GET request to the endpoint
    response = client.get('/courier_data')

    # Assert successful response
    assert response.status_code == 200

    # Parse the JSON response
    data = response.get_json()

    # Assert the response is a list
    assert isinstance(data, list), "Response is not a list"

    # Validate that each record has the expected structure
    for record in data:
        assert isinstance(record, dict), "Record is not a dictionary"
        assert 'courier_id' in record, "Missing 'courier_id'"
        assert 'order_id' in record, "Missing 'order_id'"
        assert 'name' in record, "Missing 'name'"
        assert 'status' in record, "Missing 'status'"
        assert 'date' in record, "Missing 'date'"

    # Optional: Log the first few records (helpful during debugging)
    if len(data) > 0:
        print("Sample record:", data[0])
