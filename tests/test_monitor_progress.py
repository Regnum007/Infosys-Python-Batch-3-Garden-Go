import pytest
from  app import app  # Use double dots to go up one level
# Test client setup
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_delivered_orders_tile(client):
    response = client.get('/monitor_progress')
    assert b"Delivered Orders" in response.data
    assert b"<p>" in response.data and b"80" in response.data 

# Test: Charts Section
def test_line_chart_rendering(client):
    response = client.get('/monitor_progress')
    assert b"Deliveries Over Time" in response.data
    assert b"<div>" in response.data  # Check if the chart HTML is rendered.

def test_bar_chart_rendering(client):
    response = client.get('/monitor_progress')
    assert b"Delivery Status Distribution" in response.data
    assert b"<div>" in response.data  # Check if the chart HTML is rendered.


# Test: Navigation
def test_back_to_form_link(client):
    response = client.get('/monitor_progress')
    assert b'<a href="/">Back to Form</a>' in response.data




