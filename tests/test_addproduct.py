import os
import tempfile
from flask import Flask, request, url_for
import pytest

@pytest.fixture
def app():
    """Fixture to configure the Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

    # Register routes
    @app.route('/admin/add_product', methods=['GET', 'POST'])
    def add_product():
        if request.method == 'POST':
            name = request.form.get('name')
            category_name = request.form.get('category_name')
            description = request.form.get('description')
            image_url = request.form.get('image_url')
            image_file = request.files.get('image_file')
            weight = request.form.get('weight')
            selling_price = request.form.get('selling_price')
            stock_quantity = request.form.get('stock_quantity')

            # Validate inputs
            if not all([name, category_name, description, weight, selling_price, stock_quantity]):
                return "Missing fields", 400

            # Handle file upload if provided
            if image_file:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
                image_file.save(file_path)

            return "Product added successfully", 200

        return '''
        <form method="POST" enctype="multipart/form-data">
            <!-- Add form fields here -->
        </form>
        '''

    return app

@pytest.fixture
def client(app):
    """Fixture to provide a test client for the Flask app."""
    return app.test_client()

def test_add_product_get(client):
    """Test GET request for the add product page."""
    response = client.get('/admin/add_product')
    assert response.status_code == 200
    assert b'<form' in response.data  # Check if the form is present

def test_add_product_post_valid(client):
    """Test POST request with valid data."""
    data = {
        'name': 'Test Product',
        'category_name': 'Electronics',
        'description': 'Test description',
        'weight': '1.5',
        'selling_price': '999.99',
        'stock_quantity': '10',
    }
    files = {
        'image_file': (tempfile.NamedTemporaryFile(suffix=".jpg"), 'test_image.jpg')
    }

    response = client.post('/admin/add_product', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'Product added successfully' in response.data

def test_add_product_post_missing_field(client):
    """Test POST request with missing fields."""
    data = {
        'name': '',
        'category_name': 'Electronics',
        'description': 'Test description',
        'weight': '1.5',
        'selling_price': '999.99',
        'stock_quantity': '10',
    }

    response = client.post('/admin/add_product', data=data, follow_redirects=True)
    assert response.status_code == 400
    assert b'Missing fields' in response.data

def test_add_product_post_file_upload(client):
    """Test POST request with file upload."""
    data = {
        'name': 'Test Product',
        'category_name': 'Electronics',
        'description': 'Test description',
        'weight': '1.5',
        'selling_price': '999.99',
        'stock_quantity': '10',
    }
    files = {
        'image_file': (tempfile.NamedTemporaryFile(suffix=".jpg"), 'test_image.jpg')
    }

    response = client.post('/admin/add_product', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'Product added successfully' in response.data
