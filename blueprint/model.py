from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, timezone


app = Flask(__name__)

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# User model
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255))
    roles = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    orders = db.relationship('Order', backref='user')
    notifications = db.relationship('Notification', backref='user')
    issues = db.relationship('DeliveryIssue', backref='user')


# Category model with product_names field
class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))

    products = db.relationship('Product', backref='category_link', lazy='dynamic')  # Renamed to 'category_link'

    # This field stores product names as a comma-separated list
    product_names = db.Column(db.String(255))  # List of product names


# Product model with category_name
class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    category_name = db.Column(db.String(100))  # Directly store category name here
    cost_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    weight = db.Column(db.Float)
    stock_quantity = db.Column(db.Integer)
    
    image_url = db.Column(db.String(255))
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)

    order_details = db.relationship('OrderDetail', backref='product')


# Order model
class Order(db.Model):
    __tablename__ = 'order'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    orderDate = db.Column(db.DateTime, default=datetime.utcnow)
    totalWeight = db.Column(db.Float)
    ShippingCost = db.Column(db.Float)
    status = db.Column(db.String(50))
    ShippingAddress = db.Column(db.String(255))
    TotalPayment = db.Column(db.Float)

    order_details = db.relationship('OrderDetail', backref='order')
    notifications = db.relationship('Notification', backref='order')


# OrderDetail model
class OrderDetail(db.Model):
    __tablename__ = 'orderdetails'
    orderDetail_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer)
    sub_Total = db.Column(db.Float)


# Notification model
class Notification(db.Model):
    __tablename__ = 'notification'
    notification_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    notification_type = db.Column(db.String(50))
    sent_time_stamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))


# DeliveryIssue model
class DeliveryIssue(db.Model):
    __tablename__ = 'delivery_issue'
    issue_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    description = db.Column(db.String(255))
    reported_dte = db.Column(db.DateTime, default=datetime.utcnow)
    courier_id = db.Column(db.Integer, db.ForeignKey('courier.courier_id'))
    resolve_status = db.Column(db.String(50))


# Courier model
class Courier(db.Model):
    __tablename__ = 'courier'
    courier_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    delivery_time = db.Column(db.DateTime)
    courier_name = db.Column(db.String(100))
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))

    delivery_issues = db.relationship('DeliveryIssue', backref='courier')


# PasswordResetToken model
class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    token_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    token = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

def convert_to_kg(weight_value):
    if 'g' in weight_value:
        return float(weight_value.replace('g', '').strip()) / 1000  # Convert grams to kilograms
    if 'kg' in weight_value:
        return float(weight_value.replace('kg', '').strip())  # Already in kilograms
    return 0.0  # Default to 0 if no valid unit is provided

def seed_products():
    with db.session.begin():
        for product in products:
            # Clean weight and convert it to float
            weight_value = product['weight']
            if isinstance(weight_value, str):
                weight_value = ''.join([char for char in weight_value if char.isdigit() or char == '.'])

            try:
                weight_value = float(weight_value)
            except ValueError:
                weight_value = 0.0

            # Handle category seeding
            category = Category.query.filter_by(name=product['category']).first()
            if not category:
                category = Category(name=product['category'])
                db.session.add(category)  # Add category to session, but don't commit yet

            # Handle product seeding
            existing_product = Product.query.filter_by(name=product['name']).first()
            if not existing_product:
                new_product = Product(
                    name=product['name'],
                    description=product['description'],
                    category_id=category.category_id,
                    category_name=category.name,
                    cost_price=product['price'],
                    selling_price=product['price'],
                    weight=weight_value,
                    stock_quantity=product['stock'],
                    added_date=datetime.now(timezone.utc),
                    updated_date=datetime.now(timezone.utc),
                    image_url=product['image']
                )
                db.session.add(new_product)  # Add product to session, but don't commit yet

        # Commit once after processing all products
        db.session.commit()

    print("Products seeded successfully!")

# Example product data for seeding
products = [
    {
        'name': 'Yarrow',
        'description': 'A flowering herb often used for its medicinal properties.',
        'image': 'yarrow.jpg',
        'price': 15.0,
        'weight': '100g',
        'category': 'Wild edible plants',
        'stock': 50,
        'uses': 'Promotes wound healing and aids in digestion.',
        'product_code': 'YAR123'
    },
    {
        'name': 'Chickweed',
        'description': 'A small plant known for its use in herbal remedies and salads.',
        'image': 'chick.jpg',
        'price': 12.0,
        'weight': '150g',
        'category': 'Wild edible plants',
        'stock': 60,
        'uses': 'Helps soothe skin irritations and supports respiratory health.',
        'product_code': 'CHI123'
    },
    {
        'name': 'Comfrey',
        'description': 'A medicinal herb traditionally used to promote healing.',
        'image': 'comfrey.jpg',
        'price': 18.0,
        'weight': '200g',
        'category': 'Wild edible plants',
        'stock': 40,
        'uses': 'Supports bone healing and reduces inflammation.',
        'product_code': 'COM123'
    },
    {
        'name': 'Dead Nettle',
        'description': 'An edible plant with anti-inflammatory properties.',
        'image': 'deadnettle.jpg',
        'price': 140.0,
        'weight': '180g',
        'category': 'Wild edible plants',
        'stock': 55,
        'uses': 'Provides relief for arthritis and soothes skin conditions.',
        'product_code': 'DNT123'
    },
    {
        'name': 'Nettle',
        'description': 'A nutrient-rich plant known for its anti-inflammatory benefits.',
        'image': 'nettle.jpg',
        'price': 160.0,
        'weight': '110g',
        'category': 'Wild edible plants',
        'stock': 45,
        'uses': 'Improves joint health and acts as a natural detoxifier.',
        'product_code': 'NET123'
    },
    {
        'name': 'Basil Black Seeds',
        'description': 'Rich in nutrients and used in herbal medicine.',
        'image': 'Basilblackseeds.jpeg',
        'price': 300.0,
        'weight': '120g',
        'category': 'seeds',
        'stock': 100,
        'uses': 'Boosts immunity and promotes digestion.',
        'product_code': 'BAS123'
    },
    {
        'name': 'Neem Seeds',
        'description': 'Used in traditional medicine and natural pesticides.',
        'image': 'Neemseeds.jpeg',
        'price': 12.0,
        'weight': '150g',
        'category': 'Seeds',
        'stock': 90,
        'uses': 'Acts as a natural pesticide and supports skin health.',
        'product_code': 'NEM123'
    },
    {
        'name': 'Ashwagandha Seeds',
        'description': 'Known for its adaptogenic properties.',
        'image': 'Ashwagandhaseeds.jpeg',
        'price': 15.0,
        'weight': '200g',
        'category': 'Seeds',
        'stock': 80,
        'uses': 'Reduces stress and improves energy levels.',
        'product_code': 'ASH123'
    },
    {
        'name': 'Lemon Balm Seeds',
        'description': 'Popular for its calming effects.',
        'image': 'Lemonbalmseeds.jpeg',
        'price': 14.0,
        'weight': '100g',
        'category': 'Seeds',
        'stock': 700,
        'uses': 'Promotes relaxation and supports digestion.',
        'product_code': 'LEM123'
    },
    {
        'name': 'Red Sandalwood Seeds',
        'description': 'Valued for its medicinal properties.',
        'image': 'Redsandalwoodseeds.jpeg',
        'price': 20.0,
        'weight': '90g',
        'category': 'Seeds',
        'stock': 60,
        'uses': 'Supports skin health and reduces inflammation.',
        'product_code': 'RSW123'
    },
    {
        'name': 'Costus',
        'description': 'A medicinal plant used in traditional healing.',
        'image': 'Costus.jpg',
        'price': 25.0,
        'weight': '150g',
        'category': 'Plants',
        'stock': 70,
        'uses': 'Boosts immunity and aids in respiratory health.',
        'product_code': 'COS123'
    },
     {
        'name': 'Globe Artichoke',
        'description': 'A perennial thistle cultivated for its edible flower buds.',
        'image': 'Globoartichoke.jpg',
        'price': 18.0,
        'weight': '180g',
        'category': 'Plants',
        'stock': 65,
        'uses': 'Supports liver health and improves digestion.',
        'product_code': 'GLO123'
    },
    {
        'name': 'Fenugreek',
        'description': 'A green forage plant rich in nutrients.',
        'image': 'fenugreek-greenforage_480x480.jpg',
        'price': 14.0,
        'weight': '200g',
        'category': 'Plants',
        'stock': 75,
        'uses': 'Promotes lactation and reduces inflammation.',
        'product_code': 'FEN123'
    },
    {
        'name': 'German Chamomile',
        'description': 'An aromatic herb known for its calming properties.',
        'image': 'Germanchamomile.jpg',
        'price': 12.0,
        'weight': '100g',
        'category': 'Plants',
        'stock': 85,
        'uses': 'Supports relaxation and improves sleep.',
        'product_code': 'GER123'
    },
    {
        'name': 'Lavender',
        'description': 'A fragrant herb used for its soothing effects.',
        'image': 'Lavender.jpg',
        'price': 20.0,
        'weight': '90g',
        'category': 'Plants',
        'stock': 55,
        'uses': 'Reduces stress and enhances skin health.',
        'product_code': 'LAV123'
    },
    {
        'name': 'Calendula',
        'description': 'A flowering plant valued for its anti-inflammatory benefits.',
        'image': 'Calendula.jpg',
        'price': 15.0,
        'weight': '120g',
        'category': 'Plants',
        'stock': 60,
        'uses': 'Aids in wound healing and skin care.',
        'product_code': 'CAL123'
    },
    {
        'name': 'Gotu Kola',
        'description': 'A traditional herb known for its cognitive benefits.',
        'image': 'Gotu kola.jpg',
        'price': 16.0,
        'weight': '130g',
        'category': 'Plants',
        'stock': 50,
        'uses': 'Enhances memory and promotes circulation.',
        'product_code': 'GOT123'
    },
    {
        'name': 'Aloe Vera',
        'description': 'A succulent plant used for skin and digestive health.',
        'image': 'Aloevera.jpg',
        'price': 22.0,
        'weight': '140g',
        'category': 'Plants',
        'stock': 90,
        'uses': 'Soothes burns and supports digestion.',
        'product_code': 'ALO123'
    },
    {
        'name': 'Tulsi',
        'description': 'A sacred plant known for its adaptogenic properties.',
        'image': 'Tulsi.jpg',
        'price': 13.0,
        'weight': '110g',
        'category': 'Plants',
        'stock': 100,
        'uses': 'Boosts immunity and reduces stress.',
        'product_code': 'TUL123'
    },
    {
        'name': 'Stevia',
        'description': 'A natural sweetener plant.',
        'image': 'Stevia.jpg',
        'price': 11.0,
        'weight': '150g',
        'category': 'Plants',
        'stock': 95,
        'uses': 'Used as a sugar substitute and supports blood sugar balance.',
        'product_code': 'STE123',
        
    }
    # Add other products here...
]


# Main execution
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables
        seed_products()  # Seed the database with product data
    print("Database setup and seeding complete!")
