import pytest
from flask import Flask, render_template, request

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = Flask(__name__)

    # Mock todos data
    todos = {
        1: {
            "sno": 1,
            "orderid": 101,
            "courier_name": "FastCourier",
            "status": "Dispatched"
        }
    }

    @app.route('/update/<int:sno>', methods=['GET', 'POST'])
    def update_status(sno):
        try:
            todo = todos.get(sno)
            if not todo:
                return "Todo not found", 404

            if request.method == "POST":
                try:
                    orderid = int(request.form.get("orderid")) 
                except ValueError:
                    return "Invalid order ID", 400 

                todo["courier_name"] = request.form.get("courier_name") 
                todo["status"] = request.form.get("status") 
                return "Status Updated", 200

            return render_template("update.html", todo=todo)  # Assuming update.html exists

        except Exception as e:
            app.logger.error(f"An error occurred in update_status: {e}") 
            return "Internal Server Error", 500 

    return app

@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    with app.test_client() as client:
        yield client

def test_update_status_successful_update(client):
    """Test successful update of todo item."""
    try:
        response = client.post('/update/1', data={
            "orderid": 102, 
            "courier_name": "NewCourier",
            "status": "Delivered"
        })
        assert response.status_code == 200
        assert response.data.decode() == "Status Updated"
    except Exception as e:
        print(f"Error in test_update_status_successful_update: {e}")
        raise e

if __name__ == "__main__":
    pytest.main()