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
        # Fetch delivered orders only
        orders = Order.query.filter(Order.status == "Delivered").all()

        daily_data = {}
        monthly_data = {}
        yearly_data = {}

        for order in orders:
            if order.delivery_date and order.expected_delivery_date:
                date_str = order.delivery_date.strftime('%Y-%m-%d')
                month_str = order.delivery_date.strftime('%Y-%m')
                year_str = order.delivery_date.strftime('%Y')

                # Determine if order is on-time or late
                status = "On-Time" if order.delivery_status == "On-Time" else "Late"

                # Daily Aggregation
                if date_str not in daily_data:
                    daily_data[date_str] = {"On-Time": 0, "Late": 0}
                daily_data[date_str][status] += 1

                # Monthly Aggregation
                if month_str not in monthly_data:
                    monthly_data[month_str] = {"On-Time": 0, "Late": 0}
                monthly_data[month_str][status] += 1

                # Yearly Aggregation
                if year_str not in yearly_data:
                    yearly_data[year_str] = {"On-Time": 0, "Late": 0}
                yearly_data[year_str][status] += 1

        response_data = {
            "daily": daily_data,
            "monthly": monthly_data,
            "yearly": yearly_data
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500





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
        
REGIONS = {
    "North": range(110000, 300000),
    "South": range(500001, 700000),
    "East": range(700001, 999999),
    "West": range(400001, 500000),
    "Central": range(300000, 400000)
}

def get_region(postal_code):
    for region, pincodes in REGIONS.items():
        if int(postal_code) in pincodes:
            return region
    return "Unknown"

@analystt4.route('/regional_popular_products')
def regional_popular_products():
    region_products = {region: [] for region in REGIONS.keys()}

    # Fetch orders along with their region based on the user's address
    order_data = (
        db.session.query(
            Address.postal_code,  # Get postal code from Address table
            OrderDetail.product_id, 
            func.sum(OrderDetail.quantity).label('total_sold')
        )
        .join(Order, Order.order_id == OrderDetail.order_id)  # Join Orders to OrderDetails
        .join(User, Order.user_id == User.user_id)  # Join Orders to Users
        .join(
            Address, 
            (Address.user_id == User.user_id) & 
            (Address.created_at <= Order.created_at)  # Get address valid at order time
        )
        .group_by(Address.postal_code, OrderDetail.product_id)
        .all()
    )

    # Categorize product sales into regions
    region_sales = {region: {} for region in REGIONS.keys()}

    for postal_code, product_id, total_sold in order_data:
        region = get_region(postal_code)  # Determine region using postal code
        if region in region_sales:
            region_sales[region][product_id] = region_sales[region].get(product_id, 0) + total_sold

    # Get product details for the top 5 products per region
    for region, sales in region_sales.items():
        sorted_products = sorted(sales.items(), key=lambda x: x[1], reverse=True)[:5]  # Top 5
        product_ids = [product_id for product_id, _ in sorted_products]

        # Fetch product details
        products = db.session.query(
            Product.product_id, 
            Product.name, 
            Product.image_url, 
            Product.selling_price
        ).filter(Product.product_id.in_(product_ids)).all()

        # Convert to dictionary format required for the template
        region_products[region] = [
            {
                "product_id": p.product_id,
                "name": p.name,
                "image_url": p.image_url,
                "selling_price": p.selling_price,
                "order_count": sales.get(p.product_id, 0)  # Add order count for chart
            }
            for p in products
        ]

    return render_template('regional_popular_products.html', region_products=region_products)



