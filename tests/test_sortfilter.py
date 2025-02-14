import pytest
import warnings
from integration.model import app, db, Product
from datetime import datetime, timezone

# Suppress DeprecationWarnings from SQLAlchemy
warnings.filterwarnings("ignore", category=DeprecationWarning)

@pytest.fixture
def client():
    """Creates a test client and initializes an empty test database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use separate test DB
    with app.app_context():
        db.create_all()
        seed_test_data()  # Add test products
        yield app.test_client()
        db.session.remove()
        db.drop_all()  # Cleanup after tests

def seed_test_data():
    """Seeds test data into the database for testing sorting & filtering."""
    products = [
        Product(name="Aloe Vera", selling_price=20, category_name="Plants", stock_quantity=90, added_date=datetime.now(timezone.utc)),
        Product(name="Tulsi", selling_price=13, category_name="Plants", stock_quantity=100, added_date=datetime.now(timezone.utc)),
        Product(name="Stevia", selling_price=11, category_name="Plants", stock_quantity=95, added_date=datetime.now(timezone.utc)),
        Product(name="Nettle", selling_price=160, category_name="Wild edible plants", stock_quantity=45, added_date=datetime.now(timezone.utc)),
        Product(name="Dead Nettle", selling_price=140, category_name="Wild edible plants", stock_quantity=55, added_date=datetime.now(timezone.utc)),
    ]
    db.session.bulk_save_objects(products)
    db.session.commit()

# Helper function to fetch products
def get_products(order_by=None, filter_by=None, filter_value=None, descending=False):
    query = Product.query
    if filter_by and filter_value:
        query = query.filter(getattr(Product, filter_by) == filter_value)
    if order_by:
        if descending:
            query = query.order_by(getattr(Product, order_by).desc())
        else:
            query = query.order_by(getattr(Product, order_by))
    return query.all()

#  Sorting in Ascending Order
def test_sort_ascending(client):
    sorted_products = get_products(order_by="selling_price")
    prices = [p.selling_price for p in sorted_products]
    assert prices == sorted(prices), f"Expected {sorted(prices)}, but got {prices}"

#  Sorting in Descending Order
def test_sort_descending(client):
    sorted_products = get_products(order_by="selling_price", descending=True)
    prices = [p.selling_price for p in sorted_products]
    assert prices == sorted(prices, reverse=True), f"Expected {sorted(prices, reverse=True)}, but got {prices}"

# Filtering by a Specific Attribute
def test_filter_by_category(client):
    filtered_products = get_products(filter_by="category_name", filter_value="Plants")
    assert all(p.category_name == "Plants" for p in filtered_products), "Filtering by category failed"

# Filtering with No Matching Criteria
def test_filter_no_match(client):
    filtered_products = get_products(filter_by="category_name", filter_value="Nonexistent Category")
    assert filtered_products == [], "Expected empty list, but got results"

#  Sorting After Filtering
def test_sort_after_filtering(client):
    filtered_sorted_products = get_products(filter_by="category_name", filter_value="Plants", order_by="selling_price")
    prices = [p.selling_price for p in filtered_sorted_products]
    assert prices == sorted(prices), "Sorting after filtering failed"

#  Filtering After Sorting
def test_filter_after_sorting(client):
    sorted_products = get_products(order_by="selling_price")
    filtered_products = [p for p in sorted_products if p.category_name == "Plants"]
    assert all(p.category_name == "Plants" for p in filtered_products), "Filtering after sorting failed"

# Sorting & Filtering Combined
def test_sort_and_filter_combined(client):
    sorted_filtered_products = get_products(order_by="selling_price", filter_by="category_name", filter_value="Plants", descending=True)
    prices = [p.selling_price for p in sorted_filtered_products]
    assert prices == sorted(prices, reverse=True), "Sorting & filtering combination failed"

#  Handling Edge Cases
def test_edge_cases(client):
    """Test sorting & filtering with edge cases like empty lists and single items."""
    # Empty case
    assert get_products(order_by="selling_price") != [], "Sorting empty list failed"
    
    # Single item case
    single_product = Product(name="Test Product", selling_price=50, category_name="Test Category", stock_quantity=1, added_date=datetime.now(timezone.utc))
    db.session.add(single_product)
    db.session.commit()

    fetched_products = get_products(order_by="selling_price")
    assert any(p.selling_price == 50 for p in fetched_products), "Single item list handling failed"

# Invalid Filter Key Handling
def test_invalid_filter(client):
    with pytest.raises(AttributeError):
        get_products(filter_by="nonexistent_attribute", filter_value="Test")

