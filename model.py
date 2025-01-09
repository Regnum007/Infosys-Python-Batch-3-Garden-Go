from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
import pytz
import uuid


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

IST = pytz.timezone('Asia/Kolkata')

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('Customer', 'Admin', 'Courier'), default='Customer', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(IST), onupdate=lambda: datetime.now(IST))
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    reset_tokens = db.relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    addresses = db.relationship("Address", back_populates="user", cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='user')
    notifications = db.relationship('Notification', backref='user')
    issues = db.relationship('DeliveryIssue', backref='user')

    def __init__(self, name, email, phone_number, password, role='Customer'):
        self.name = name.title()
        self.email = email.lower()
        self.phone_number = phone_number
        self.set_password(password)
        self.role = role.title()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))

    products = db.relationship('Product', backref='category_link', lazy='dynamic')


class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    category_name = db.Column(db.String(100))
    cost_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    weight = db.Column(db.Float)
    stock_quantity = db.Column(db.Integer)
    is_deleted = db.Column(db.Boolean, default=False)

    image_url = db.Column(db.String(255))
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)

    


class Order(db.Model):
    __tablename__ = 'order'
    
    order_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    quantities = db.Column(db.Float, nullable=False)
    prices = db.Column(db.Float, nullable=False)

    order_details = db.relationship('OrderDetail', backref='order')
    notifications = db.relationship('Notification', backref='order')

class OrderDetail(db.Model):
    __tablename__ = 'orderdetails'
    orderDetail_id = db.Column(db.String(36), primary_key=True,default=lambda:str(uuid.uuid4()))
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer)
    sub_Total = db.Column(db.Float)

    
    product = db.relationship('Product', backref='order_details')




class Notification(db.Model):
    __tablename__ = 'notification'
    notification_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    notification_type = db.Column(db.String(50))
    sent_time_stamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))


class DeliveryIssue(db.Model):
    __tablename__ = 'delivery_issue'
    issue_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    description = db.Column(db.String(255))
    reported_dte = db.Column(db.DateTime, default=datetime.utcnow)
    courier_id = db.Column(db.Integer, db.ForeignKey('courier.order_id'))
    resolve_status = db.Column(db.String(50))


class Courier(db.Model):
    __tablename__ = 'courier'
    courier_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    delivery_time = db.Column(db.DateTime)
    courier_name = db.Column(db.String(100))
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))

    delivery_issues = db.relationship('DeliveryIssue', backref='courier')

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    token_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST), nullable=False)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.now(IST) + timedelta(minutes=15), nullable=False)
    user = db.relationship("User", back_populates="reset_tokens")

class Sales(db.Model):
    __tablename__= 'sales'
    sales_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    units_sold = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Numeric(10, 2), nullable=False)
    profit = db.Column(db.Numeric(10, 2), nullable=False)
    sales_date = db.Column(db.DateTime, nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
 

class Address(db.Model):
    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    street_address = db.Column(db.String, nullable=False)
    locality = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=True)
    postal_code = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", back_populates="addresses")



    
def convert_to_kg(weight_value):
    if 'g' in weight_value:
        return float(weight_value.replace('g', '').strip()) / 1000 
    if 'kg' in weight_value:
        return float(weight_value.replace('kg', '').strip())  
    return 0.0  

def seed_products():
    with db.session.begin():
        for product in products:
            
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
                db.session.add(new_product)  

       
        db.session.commit()

    print("Products seeded successfully!")
class DeletedProduct(db.Model):
    __tablename__ = 'deleted_products'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description =db. Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    weight = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
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
        
        
    }
    
]
def seed_data():
    # Seed Categories
    categories = set(product['category'] for product in products)
    category_dict = {}
    
    for category_name in categories:
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()  
        category_dict[category_name] = category.category_id

   
    for product in products:
        existing_product = Product.query.filter_by(name=product['name']).first()
        if not existing_product:
            new_product = Product(
                name=product['name'],
                description=product['description'],
                category_id=category_dict[product['category']],
                category_name=product['category'],
                cost_price=product['price'],
                selling_price=product['price'] * 1.2,  
                weight=convert_to_kg(product['weight']),
                stock_quantity=product['stock'],
                added_date=datetime.now(timezone.utc),
                updated_date=datetime.now(timezone.utc),
                image_url=product['image']
            )
            db.session.add(new_product)

    
    for sale in sales_data:
        existing_sale = Sales.query.filter_by(sales_date=sale['sales_date']).first()
        if not existing_sale:
            new_sale = Sales(
                product_id=sale['product_id'],
                units_sold=sale['units_sold'],
                revenue=sale['revenue'],
                profit=sale['profit'],
                sales_date=sale['sales_date']
            )
            db.session.add(new_sale)

    db.session.commit()
    print("Seeding completed successfully!")


sales_data = [
    {"product_id": 1, "units_sold": 100, "revenue": 10000.00, "profit": 2000.00, "sales_date": datetime(2024, 1, 1)},
    {"product_id": 2, "units_sold": 50, "revenue": 5000.00, "profit": 1500.00, "sales_date": datetime(2024, 1, 2)},
    {"product_id": 3, "units_sold": 75, "revenue": 7500.00, "profit": 2500.00, "sales_date": datetime(2024, 1, 3)},
    {"product_id": 4, "units_sold": 120, "revenue": 12000.00, "profit": 3000.00, "sales_date": datetime(2024, 1, 4)},
    {"product_id": 5, "units_sold": 90, "revenue": 9000.00, "profit": 1800.00, "sales_date": datetime(2024, 1, 5)},
    {"product_id": 6, "units_sold": 30, "revenue": 3000.00, "profit": 1000.00, "sales_date": datetime(2024, 1, 6)},
    {"product_id": 7, "units_sold": 200, "revenue": 20000.00, "profit": 5000.00, "sales_date": datetime(2024, 1, 7)},
    {"product_id": 8, "units_sold": 60, "revenue": 6000.00, "profit": 1200.00, "sales_date": datetime(2024, 1, 8)},
    {"product_id": 9, "units_sold": 80, "revenue": 8000.00, "profit": 1600.00, "sales_date": datetime(2024, 1, 9)},
    {"product_id": 10, "units_sold": 150, "revenue": 15000.00, "profit": 4000.00, "sales_date": datetime(2024, 1, 10)},
    {"product_id": 11, "units_sold": 110, "revenue": 11000.00, "profit": 2200.00, "sales_date": datetime(2024, 1, 11)},
    {"product_id": 12, "units_sold": 95, "revenue": 9500.00, "profit": 1900.00, "sales_date": datetime(2024, 1, 12)},
    {"product_id": 13, "units_sold": 40, "revenue": 4000.00, "profit": 800.00, "sales_date": datetime(2024, 1, 13)},
    {"product_id": 14, "units_sold": 175, "revenue": 17500.00, "profit": 3500.00, "sales_date": datetime(2024, 1, 14)},
    {"product_id": 15, "units_sold": 85, "revenue": 8500.00, "profit": 1700.00, "sales_date": datetime(2024, 1, 15)},
]







if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
        seed_products() 
        seed_data()
    print("Database setup and seeding complete!")
