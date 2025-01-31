from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session,Blueprint
from datetime import datetime
from model import User, Address, Sales, Courier,Order,db,OrderDetail, DeliveryTimingStatus,DeliveryIssue,Product
   
import logging
from logging.config import fileConfig

from flask import current_app
from utils import admin_required

from alembic import context
from flask_cors import CORS  # Import CORS from flask_cors
from sqlalchemy import func, extract
from flask_migrate import Migrate
from model import Order, OrderDetail, Product, seed_orders
analystt4 = Blueprint("analystt4", __name__, static_folder="static", template_folder="templates")

CORS(analystt4)
# Admin credentials
admin_credentials = {
    "username": "admin",
    "password": "password123"  # Replace with a secure password
}

@analystt4.route('/analyticsindex')
@admin_required
def analyticsindex():
    try:
        return render_template('analyst.html')
    except Exception as e:
        return f"An error occurred while loading the index: {e}", 500

@analystt4.route('/loginananalytics', methods=['GET', 'POST'])
@admin_required
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == admin_credentials['username'] and password == admin_credentials['password']:
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')  # Render login page again on failure

@analystt4.route('/logout')
@admin_required
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@analystt4.route('/sales_graph')
@admin_required
def sales_graph():
    try:
        # Fetch sales data from the database
        sales_data = Sales.query.all()
        return render_template('sales_graph.html', sales_data=sales_data)
    except Exception as e:
        return f"An error occurred while loading the sales graph: {e}", 500


@analystt4.route('/delivery_dashboard')
@admin_required
def delivery_dashboard():
    try:
        return render_template('delivery_dashboard.html')
    except Exception as e:
        return f"An error occurred while loading the delivery dashboard: {e}", 500

@analystt4.route('/api/delivery-data')
@admin_required
def get_delivery_data():
    try:
        # Just get all couriers first
        couriers = Courier.query.all()

        delivery_data = []
        for courier in couriers:
            if courier.delivery_time:  # Only include if there's a delivery time
                delivery_data.append({
                    'date': courier.delivery_time.strftime('%Y-%m-%d'),
                    'deliveryTime': courier.delivery_time.hour,  # Just using hour for now
                    'onTime': courier.delivery_timing == DeliveryTimingStatus.ON_TIME
                })

        print(f"Sending {len(delivery_data)} records")  # Debug print
        return jsonify(delivery_data)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analystt4.route('/product_heat_maps')
@admin_required
def product_heat_maps():
    try:
        return render_template('heat_maps_updated.html')
    except Exception as e:
        return f"An error occurred while loading the product heat maps: {e}", 500


@analystt4.route('/api/product-list')
@admin_required
def get_product_list():
    try:
        # Get list of all product names
        products = Product.query.with_entities(Product.name).all()
        return jsonify([product[0] for product in products])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@analystt4.route('/api/product-popularity')
@admin_required
def get_product_popularity():
    try:
        product_name = request.args.get('product')
        print(f"Received request for product: {product_name}")

        if not product_name:
            return jsonify({"error": "Product name is required"}), 400

        # Get the product first to ensure it exists
        product = Product.query.filter_by(name=product_name).first()
        if not product:
            print(f"Product not found: {product_name}")
            return jsonify({"error": f"Product not found: {product_name}"}), 404

        print(f"Found product with ID: {product.product_id}")

        # Define regions with their states and cities
        region_mapping = {
            "Region 1": {
                "states": ["Delhi", "Uttar Pradesh", "Punjab", "Haryana", "Rajasthan"],
                "cities": ["Delhi", "Lucknow", "Chandigarh", "Amritsar", "Jaipur", "Kanpur", "Varanasi", "Dehradun"]
            },
            "Region 2": {
                "states": ["Tamil Nadu", "Karnataka", "Andhra Pradesh", "Telangana", "Kerala"],
                "cities": ["Chennai", "Bangalore", "Hyderabad", "Kochi", "Mysore", "Vijayawada", "Trivandrum", "Madurai"]
            },
            "Region 3": {
                "states": ["West Bengal", "Odisha", "Bihar", "Jharkhand", "Assam"],
                "cities": ["Kolkata", "Bhubaneswar", "Guwahati", "Patna", "Ranchi", "Shillong", "Durgapur", "Siliguri"]
            },
            "Region 4": {
                "states": ["Maharashtra", "Gujarat", "Goa"],
                "cities": ["Mumbai", "Pune", "Ahmedabad", "Surat", "Nagpur", "Goa", "Vadodara", "Udaipur"]
            },
            "Region 5": {
                "states": ["Madhya Pradesh", "Chhattisgarh"],
                "cities": ["Bhopal", "Indore", "Raipur", "Gwalior", "Jabalpur", "Bilaspur", "Ujjain", "Rewa"]
            }
        }

        popularity_data = []

        # Print debug information about data availability
        print(f"Database counts:")
        print(f"Users: {User.query.count()}")
        print(f"Addresses: {Address.query.count()}")
        print(f"Orders: {Order.query.count()}")
        print(f"Order Details: {OrderDetail.query.count()}")

        for region_number in range(1, 6):
            region_key = f"Region {region_number}"
            region_states = region_mapping[region_key]["states"]
            region_cities = region_mapping[region_key]["cities"]

            try:
                # Query to get total quantity of the product sold in this region
                region_popularity = (
                    db.session.query(func.coalesce(func.sum(OrderDetail.quantity), 0))
                    .join(Order, OrderDetail.order_id == Order.order_id)
                    .join(User, Order.user_id == User.user_id)
                    .join(Address, User.user_id == Address.user_id)
                    .filter(
                        OrderDetail.product_id == product.product_id,
                        db.or_(
                            Address.state.in_(region_states),
                            Address.city.in_(region_cities)
                        )
                    )
                ).scalar() or 0

                print(f"Popularity for {region_key}: {region_popularity}")
                popularity_data.append(float(region_popularity))

            except Exception as e:
                print(f"Error processing region {region_key}: {e}")
                popularity_data.append(0.0)

        print(f"Final popularity data: {popularity_data}")
        return jsonify(popularity_data)

    except Exception as e:
        print(f"Error in product popularity query: {e}")
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return jsonify(error_details), 500


@analystt4.route('/home')
@admin_required
def home():
    try:
        return render_template('home.html')
    except Exception as e:
        return f"An error occurred while loading the home page: {e}", 500

@analystt4.route('/api/sales-data', methods=['GET'])
@admin_required
def get_sales_data():
    try:
        # Retrieve the query parameters for filtering by month and year
        year = request.args.get('year')
        month = request.args.get('month')

        # If year and month are provided, filter by that
        if year and month:
            start_date = f"{year}-{month}-01"
            end_date = f"{year}-{month}-31"  # Assuming all months have 31 days, which is fine for range query
            daily_data = db.session.query(
                func.date(Sales.sales_date).label('date'),
                func.sum(Sales.units_sold).label('total_units'),
                func.sum(Sales.revenue).label('total_revenue'),
                func.sum(Sales.profit).label('total_profit')
            ).filter(Sales.sales_date >= start_date, Sales.sales_date <= end_date) \
             .group_by(func.date(Sales.sales_date)) \
             .all()

        # If only year is provided, filter by that
        elif year:
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            daily_data = db.session.query(
                func.date(Sales.sales_date).label('date'),
                func.sum(Sales.units_sold).label('total_units'),
                func.sum(Sales.revenue).label('total_revenue'),
                func.sum(Sales.profit).label('total_profit')
            ).filter(Sales.sales_date >= start_date, Sales.sales_date <= end_date) \
             .group_by(func.date(Sales.sales_date)) \
             .all()

        # If no filter is provided, retrieve all data
        else:
            daily_data = db.session.query(
                func.date(Sales.sales_date).label('date'),
                func.sum(Sales.units_sold).label('total_units'),
                func.sum(Sales.revenue).label('total_revenue'),
                func.sum(Sales.profit).label('total_profit')
            ).group_by(func.date(Sales.sales_date)) \
             .all()

        return jsonify([{
            "date": str(data.date),
            "sales": float(data.total_units or 0) * 100,
            "revenue": float(data.total_revenue or 0) * 10,
            "profit": float(data.total_profit or 0)
        } for data in daily_data])

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"Error occurred: {e}"}), 500



@analystt4.route('/api/generate-graph', methods=['POST'])
@admin_required
def generate_graphs():
    data = request.json
    analysis_type = data.get('analysisType')
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    year = data.get('year')

    if analysis_type == "daily" and (not start_date or not end_date):
        return jsonify({"error": "Start date and end date are required for daily analysis."}), 400
    elif analysis_type in ["monthly", "yearly"] and not year:
        return jsonify({"error": "Year is required for monthly or yearly analysis."}), 400

    try:
        filtered_data = []

        if analysis_type == "daily":
            filtered_data = Sales.query.filter(
                Sales.sales_date >= start_date, Sales.sales_date <= end_date
            ).all()
        elif analysis_type == "monthly":
            filtered_data = Sales.query.filter(Sales.sales_date.like(f'{year}-%')).all()
        elif analysis_type == "yearly":
            filtered_data = Sales.query.filter(Sales.sales_date.like(f'{year}-%')).all()

        if not filtered_data:
            return jsonify({"message": "No data available for the selected period."}), 404

        return jsonify([{
            "sales_date": sale.sales_date,
            "total_revenue": sale.revenue,
            "profit_or_loss": sale.profit
        } for sale in filtered_data])

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500


@analystt4.route('/verifyproduct')
@admin_required
def verify_product_data():
    # Check total number of products
    total_products = Product.query.count()
    print(f"Total Products: {total_products}")

    # List all product names
    products = Product.query.all()
    product_names = [product.name for product in products]
    print("Product Names:")
    for name in product_names:
        print(f"- {name}")

    # Check sales data for products
    sales_data = Sales.query.all()
    print("\nSales Data:")
    for sale in sales_data:
        product = Product.query.get(sale.product_id)
        print(f"Product: {product.name}, Units Sold: {sale.units_sold}")

    # Verify order details
    order_details = OrderDetail.query.all()
    print("\nOrder Details:")
    for detail in order_details:
        product = Product.query.get(detail.product_id)
        print(f"Product: {product.name}, Quantity: {detail.quantity}")



