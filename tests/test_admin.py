from typing import LiteralString
import pytest
import io
from flask import Flask, request, render_template_string
from flask.testing import FlaskClient
from bs4 import BeautifulSoup  # type: ignore

# Mock Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
        <title>Document</title>
    </head>
    <body>
        <div class="d-flex flex-column align-items-center justify-content-center vh-100 text-center">
            <h1 class="mb-4">You Can Edit The Product</h1>
            <div>
                <a href="/add_product" class="btn btn-primary btn-lg m-3">ADD PRODUCT</a>
                <a href="/delete_products" class="btn btn-primary btn-lg m-3">DELETE THE PRODUCT</a>
                <a href="/recovery" class="btn btn-primary btn-lg m-3">RECOVER THE DELETED PRODUCTS</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.route('/add_product')
def add_product_page():
    return "Add Product Page"

@app.route('/delete_products')
def delete_products():
    return "Delete Products Page"

@app.route('/recovery')
def recovery():
    return "Recover Deleted Products Page"

@app.route('/add', methods=['POST'])
def add_product():
    # Simulate saving the product
    product_name = request.form.get('product_name')
    category = request.form.get('category')
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    image_file = request.files.get('image_file')
    weight = request.form.get('weight')
    price = request.form.get('price')

    if not all([product_name, category, description, weight, price]):
        return "Missing required fields", 400

    return "Product added successfully", 200

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def html_content():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Product Details</title>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg bg-white">
            <a class="navbar-brand ms-2 mb-2" href="#">Courier</a>
            <ul class="navbar-nav">
                <li class="nav-item">
                    <a class="nav-link active fw-bold" href="#">Home</a>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle fw-bold ms-3" href="#" role="button">Category</a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#">Seeds</a></li>
                        <li><a class="dropdown-item" href="#">Plants</a></li>
                        <li><a class="dropdown-item" href="#">Herbs</a></li>
                    </ul>
                </li>
            </ul>
        </nav>
        <div class="container my-5">
            <div class="row">
                <div class="col-md-6">
                    <img src="/static/sample_image.jpg" alt="Product Name">
                </div>
                <div class="col-md-6">
                    <h1>Product Name</h1>
                    <p>Product Description</p>
                    <p>category : Plants</p>
                    <p>Price : $50</p>
                    <p>weight : 1kg</p>
                    <a href="#" class="btn btn-success">Buy Now</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def test_home_page(client: FlaskClient):
    response = client.get('/')
    assert response.status_code == 200
    assert b"You Can Edit The Product" in response.data

def test_add_product_page(client: FlaskClient):
    response = client.get('/add_product')
    assert response.status_code == 200
    assert b"Add Product Page" in response.data

def test_delete_products_page(client: FlaskClient):
    response = client.get('/delete_products')
    assert response.status_code == 200
    assert b"Delete Products Page" in response.data

def test_recovery_page(client: FlaskClient):
    response = client.get('/recovery')
    assert response.status_code == 200
    assert b"Recover Deleted Products Page" in response.data

def test_add_product_success(client: FlaskClient):
    data = {
        "product_name": "Test Product",
        "category": "Electronics",
        "description": "A test product description",
        "weight": "1kg",
        "price": "100"
    }
    files = {
        "image_file": (io.BytesIO(b"dummy image content"), "test_image.jpg")
    }

    response = client.post('/add', data={**data, **files}, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"Product added successfully" in response.data

def test_add_product_missing_fields(client: FlaskClient):
    data = {"product_name": "", "category": "", "description": "", "weight": "", "price": ""}
    response = client.post('/add', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"Missing required fields" in response.data

def test_navbar_links(html_content: LiteralString):
    soup = BeautifulSoup(html_content, 'html.parser')
    navbar_links = soup.find_all('a', class_='nav-link')
    assert len(navbar_links) == 2

def test_image_presence(html_content: LiteralString):
    soup = BeautifulSoup(html_content, 'html.parser')
    product_image = soup.find('img', alt="Product Name")
    assert product_image is not None
    assert product_image['src'] == "/static/sample_image.jpg"
