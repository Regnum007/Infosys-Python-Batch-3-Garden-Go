from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from faker import Faker
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
from sqlalchemy import Boolean, distinct
from enum import Enum
import pytz
import random
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
    account_request = db.Column(db.Boolean, default=False)

    reset_tokens = db.relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    addresses = db.relationship("Address", back_populates="user", cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='user')
    notifications = db.relationship('Notification', backref='user')
    delivery_issues = db.relationship('DeliveryIssue', back_populates='user')

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

class Cart(db.Model):
    __tablename__ = 'cart'

    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    is_buy_now = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product', backref='cart_items')

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
    expected_delivery_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=4), nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=True) 
    quantities = db.Column(db.Float, nullable=False)
    prices = db.Column(db.Float, nullable=False)

    order_details = db.relationship('OrderDetail', backref='order')
    notifications = db.relationship('Notification', backref='order')

class OrderDetail(db.Model):
    __tablename__ = 'orderdetails'
    orderDetail_id = db.Column(db.String(36), primary_key=True,default=lambda:str(uuid.uuid4()))
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    status = db.Column(db.String(50), default="Pending")
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

class DeliveryTimingStatus(Enum):
    ON_TIME = "on_time"
    LATE = "late"
    NOT_DELIVERED = "not_delivered"



class Sub(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.id} - {self.email}"
    

class DeliveryIssue(db.Model):
    __tablename__ = 'delivery_issue'
    issue_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), nullable=False)
    courier_id = db.Column(db.Integer, db.ForeignKey('courier.sno'))  
    description = db.Column(db.String(255))
    reported_dte = db.Column(db.DateTime, default=datetime.utcnow)
    resolve_status = db.Column(db.String(50))

    user = db.relationship('User', back_populates='delivery_issues')
    order = db.relationship('Order', backref='delivery_issues')
    courier = db.relationship('Courier', back_populates='delivery_issues')  


class Courier(db.Model):
    __tablename__ = 'courier'
    sno = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    delivery_time = db.Column(db.DateTime)
    courier_name = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_timing = db.Column(db.Enum(DeliveryTimingStatus))

    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'))
    delivery_issues = db.relationship('DeliveryIssue', back_populates='courier') 

    def __repr__(self):
        return f"{self.sno}-{self.order_id}-{self.courier_name}-{self.status}"

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    token_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    default_address = db.Column(Boolean, default=False)  

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
                    cost_price=product['cost_price'],
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
        'cost_price': 10.0, 
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
        'cost_price': 10.0,
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
        'cost_price': 10.0,
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
        'cost_price': 100.0,
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
        'cost_price': 100.0,
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
        'cost_price': 250.0,
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
        'cost_price': 10.0,
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
        'cost_price': 10.0,
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
        'cost_price': 10.0,
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
        'cost_price': 15.0,
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
        'cost_price': 20.0,
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
        'cost_price': 14.0,
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
        'cost_price': 10.0,
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
        'cost_price': 8.0,
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
        'cost_price': 15.0,
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
        'cost_price': 10.0,
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
        'cost_price': 10.0,
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
        'cost_price': 16.0,
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
        'cost_price': 10.0,
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
        'cost_price': 5.0,
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
                cost_price=product['costprice'],
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
    {"product_id": 1, "units_sold": 100, "revenue": 10000.00, "profit": 2000.00, "sales_date": datetime(2021, 1, 1)},
    {"product_id": 2, "units_sold": 50, "revenue": 5000.00, "profit": 1500.00, "sales_date": datetime(2021, 3, 2)},
    {"product_id": 3, "units_sold": 75, "revenue": 7500.00, "profit": 2500.00, "sales_date": datetime(2021, 5, 3)},
    {"product_id": 4, "units_sold": 120, "revenue": 12000.00, "profit": 3000.00, "sales_date": datetime(2021, 7, 4)},
    {"product_id": 5, "units_sold": 90, "revenue": 9000.00, "profit": 1800.00, "sales_date": datetime(2021, 9, 5)},
    {"product_id": 6, "units_sold": 30, "revenue": 3000.00, "profit": 1000.00, "sales_date": datetime(2021, 11, 6)},
    
    {"product_id": 7, "units_sold": 200, "revenue": 20000.00, "profit": 5000.00, "sales_date": datetime(2022, 2, 7)},
    {"product_id": 8, "units_sold": 60, "revenue": 6000.00, "profit": 1200.00, "sales_date": datetime(2022, 4, 8)},
    {"product_id": 9, "units_sold": 80, "revenue": 8000.00, "profit": 1600.00, "sales_date": datetime(2022, 6, 9)},
    {"product_id": 10, "units_sold": 150, "revenue": 15000.00, "profit": 4000.00, "sales_date": datetime(2022, 8, 10)},
    {"product_id": 11, "units_sold": 110, "revenue": 11000.00, "profit": 2200.00, "sales_date": datetime(2022, 10, 11)},
    {"product_id": 12, "units_sold": 95, "revenue": 9500.00, "profit": 1900.00, "sales_date": datetime(2022, 12, 12)},
    
    {"product_id": 13, "units_sold": 40, "revenue": 4000.00, "profit": 800.00, "sales_date": datetime(2023, 1, 13)},
    {"product_id": 14, "units_sold": 175, "revenue": 17500.00, "profit": 3500.00, "sales_date": datetime(2023, 2, 14)},
    {"product_id": 15, "units_sold": 85, "revenue": 8500.00, "profit": 1700.00, "sales_date": datetime(2023, 3, 15)},
    
    {"product_id": 16, "units_sold": 130, "revenue": 13000.00, "profit": 2600.00, "sales_date": datetime(2023, 5, 16)},
    {"product_id": 17, "units_sold": 90, "revenue": 9000.00, "profit": 1800.00, "sales_date": datetime(2023, 7, 17)},
    {"product_id": 18, "units_sold": 160, "revenue": 16000.00, "profit": 3200.00, "sales_date": datetime(2023, 9, 18)},
    {"product_id": 19, "units_sold": 100, "revenue": 10000.00, "profit": 2000.00, "sales_date": datetime(2023, 11, 19)},
    {"product_id": 20, "units_sold": 140, "revenue": 14000.00, "profit": 2800.00, "sales_date": datetime(2024, 1, 20)},
    
    {"product_id": 21, "units_sold": 160, "revenue": 16000.00, "profit": 3200.00, "sales_date": datetime(2024, 2, 21)},
    {"product_id": 22, "units_sold": 50, "revenue": 5000.00, "profit": 1500.00, "sales_date": datetime(2024, 3, 22)},
    {"product_id": 23, "units_sold": 110, "revenue": 11000.00, "profit": 2200.00, "sales_date": datetime(2024, 4, 23)},
    {"product_id": 24, "units_sold": 100, "revenue": 10000.00, "profit": 2000.00, "sales_date": datetime(2024, 5, 24)},
    {"product_id": 25, "units_sold": 50, "revenue": 5000.00, "profit": 1000.00, "sales_date": datetime(2024, 6, 25)}
]



def seed_user():
    if not User.query.filter_by(email='courier1160@gmail.com').first():
        courier_user = User(
            name='Go Garden courier',
            email='courier1160@gmail.com',
            phone_number=1234567890, 
            password='Courier@5544',  
            role='Courier'
        )
        db.session.add(courier_user)
        db.session.commit()
        print("Seeded courier user.")
    else:
        print("Courier user already exists.")
    if not User.query.count() >= 100:
        fake = Faker()
        users = []
        for _ in range(100):
            name = fake.name()
            email = fake.unique.email()
            phone_number = fake.unique.random_int(min=1000000000, max=9999999999)  # 10-digit phone number
            password = generate_password_hash(fake.password())
            role = 'Customer'
            created_at = fake.date_time_between(start_date="-1y")
            updated_at = created_at

            user = User(
                name=name,
                email=email,
                phone_number=phone_number,
                password=password,
                role=role
            )
            user.created_at = created_at
            user.updated_at = updated_at

            users.append(user)

        # Add users to the database session
        db.session.bulk_save_objects(users)
        db.session.commit()

        print(f"fake users have been added to the database.")


def seed_orders():
    """Seed the orders table with synthetic data"""
    # First, get all available products
    products = Product.query.all()
    if not products:
        print("No products available to create orders!")
        return

    # Create 25 orders over the last 3 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    # Generate random dates
    dates = []
    for _ in range(25):
        random_days = random.randint(0, 90)
        order_date = start_date + timedelta(days=random_days)
        dates.append(order_date)

    # Sort dates to maintain chronological order
    dates.sort()

    try:
        for i, order_date in enumerate(dates):
            # Create order with random products
            num_products = random.randint(1, 3)  # Each order has 1-3 products
            selected_products = random.sample(products, num_products)

            total_price = 0
            quantities = []
            prices = []

            # Calculate total price and prepare quantities
            for product in selected_products:
                quantity = random.randint(1, 5)
                price = product.selling_price * quantity
                total_price += price
                quantities.append(quantity)
                prices.append(price)

            # Add shipping cost
            shipping_cost = round(random.uniform(5.0, 15.0), 2)
            total_price += shipping_cost

            # Create new order
            new_order = Order(
                user_id=random.randint(1, 5),  # Assuming we have users 1-5
                total_price=total_price,
                shipping_cost=shipping_cost,
                status=random.choice(['Delivered', 'Pending', 'Shipped']),
                created_at=order_date,
                quantities=sum(quantities),
                prices=sum(prices)
            )
            db.session.add(new_order)
            db.session.flush()  # Get the order_id

            # Create order details
            for j, product in enumerate(selected_products):
                order_detail = OrderDetail(
                    order_id=new_order.order_id,
                    product_id=product.product_id,
                    quantity=quantities[j],
                    sub_Total=prices[j]
                )
                db.session.add(order_detail)

        db.session.commit()
        print(f"Successfully seeded {len(dates)} orders!")

    except Exception as e:
        db.session.rollback()
        print(f"Error seeding orders: {e}")


def seed_missing_data():
    """
    Seed users and addresses ensuring minimum 5 addresses per region.
    """
    try:
        # Get all unique user_ids from existing orders
        existing_user_ids = db.session.query(distinct(Order.user_id)).all()
        existing_user_ids = [uid[0] for uid in existing_user_ids]

        # Sample names
        first_names = ["Aarav", "Aditi", "Arjun", "Diya", "Ishaan", "Kavya", "Neha", "Pranav", "Riya", "Siddharth"]
        last_names = ["Kumar", "Singh", "Patel", "Sharma", "Verma", "Reddy", "Gupta", "Shah", "Kapoor", "Joshi"]

        # Region definitions with guaranteed address distribution
        region_addresses = {
            "Region 1": [
                {"city": "Delhi", "state": "Delhi"},
                {"city": "Jaipur", "state": "Rajasthan"},
                {"city": "Lucknow", "state": "Uttar Pradesh"},
                {"city": "Chandigarh", "state": "Punjab"},
                {"city": "Gurugram", "state": "Haryana"}
            ],
            "Region 2": [
                {"city": "Bangalore", "state": "Karnataka"},
                {"city": "Chennai", "state": "Tamil Nadu"},
                {"city": "Hyderabad", "state": "Telangana"},
                {"city": "Kochi", "state": "Kerala"},
                {"city": "Visakhapatnam", "state": "Andhra Pradesh"}
            ],
            "Region 3": [
                {"city": "Kolkata", "state": "West Bengal"},
                {"city": "Patna", "state": "Bihar"},
                {"city": "Guwahati", "state": "Assam"},
                {"city": "Bhubaneswar", "state": "Odisha"},
                {"city": "Ranchi", "state": "Jharkhand"}
            ],
            "Region 4": [
                {"city": "Mumbai", "state": "Maharashtra"},
                {"city": "Pune", "state": "Maharashtra"},
                {"city": "Ahmedabad", "state": "Gujarat"},
                {"city": "Surat", "state": "Gujarat"},
                {"city": "Panaji", "state": "Goa"}
            ],
            "Region 5": [
                {"city": "Bhopal", "state": "Madhya Pradesh"},
                {"city": "Indore", "state": "Madhya Pradesh"},
                {"city": "Raipur", "state": "Chhattisgarh"},
                {"city": "Bilaspur", "state": "Chhattisgarh"},
                {"city": "Gwalior", "state": "Madhya Pradesh"}
            ]
        }

        # First, ensure at least 5 addresses per region
        user_counter = max(existing_user_ids) + 1 if existing_user_ids else 1

        # Create guaranteed addresses for each region
        for region, addresses in region_addresses.items():
            print(f"Creating guaranteed addresses for {region}")
            for address_data in addresses:
                # Create new user
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                name = f"{first_name} {last_name}"
                email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@example.com"
                phone_number = str(random.randint(9000000000, 9999999999))

                new_user = User(
                    name=name,
                    email=email,
                    phone_number=phone_number,
                    password="password123"
                )
                db.session.add(new_user)
                db.session.flush()  # Get the user_id

                # Create address
                new_address = Address(
                    user_id=new_user.user_id,
                    street_address=f"{random.randint(1, 999)}, Main Street",
                    locality=f"Locality {random.randint(1, 5)}",
                    city=address_data["city"],
                    state=address_data["state"],
                    postal_code=random.randint(100000, 999999)
                )
                db.session.add(new_address)

        # Now add remaining users and addresses randomly
        for user_id in existing_user_ids:
            if not User.query.get(user_id):
                # Create user
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                name = f"{first_name} {last_name}"
                email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@example.com"
                phone_number = str(random.randint(9000000000, 9999999999))

                new_user = User(
                    name=name,
                    email=email,
                    phone_number=phone_number,
                    password="password123"
                )
                db.session.add(new_user)
                db.session.flush()

                # Select random region and address template
                region = random.choice(list(region_addresses.keys()))
                address_template = random.choice(region_addresses[region])

                new_address = Address(
                    user_id=new_user.user_id,
                    street_address=f"{random.randint(1, 999)}, Main Street",
                    locality=f"Locality {random.randint(1, 5)}",
                    city=address_template["city"],
                    state=address_template["state"],
                    postal_code=random.randint(100000, 999999)
                )
                db.session.add(new_address)

        db.session.commit()

        # Print distribution of addresses by region
        print("\nAddress distribution by region:")
        for region, addresses in region_addresses.items():
            states = [addr["state"] for addr in addresses]
            cities = [addr["city"] for addr in addresses]
            count = Address.query.filter(
                db.or_(
                    Address.state.in_(states),
                    Address.city.in_(cities)
                )
            ).count()
            print(f"{region}: {count} addresses")

        print("\nTotal counts:")
        print(f"Users: {User.query.count()}")
        print(f"Addresses: {Address.query.count()}")
        print(f"Orders: {Order.query.count()}")
        print(f"Order Details: {OrderDetail.query.count()}")

    except Exception as e:
        db.session.rollback()
        print(f"Error seeding data: {str(e)}")
        raise


def seed_courier_data():
    # Clear existing data
    Courier.query.delete()
    db.session.commit()

    # Start and end dates
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)

    # List of sample courier names
    courier_names = ["John Smith", "Maria Garcia", "David Chen", "Sarah Johnson",
                     "James Wilson", "Ana Rodriguez", "Michael Brown", "Emma Davis"]

    # Generate data month by month
    current_date = start_date
    order_id = 1000  # Starting order ID

    while current_date <= end_date:
        # Generate 1 or 2 entries per month
        entries_this_month = random.randint(1, 2)

        for _ in range(entries_this_month):
            # Random day and hour
            max_day = 28  # Using 28 to avoid issues with February
            delivery_day = random.randint(1, max_day)
            delivery_hour = random.randint(0, 23)
            delivery_minute = random.randint(0, 59)

            # Create delivery datetime with random hour
            delivery_date = datetime(
                current_date.year,
                current_date.month,
                delivery_day,
                hour=delivery_hour,
                minute=delivery_minute
            )

            # Random delivery timing status
            timing_status = random.choice(list(DeliveryTimingStatus))

            # Create courier entry
            courier = Courier(
                courier_name=random.choice(courier_names),
                status='delivered',
                delivery_time=delivery_date,
                order_id=order_id,
                delivery_timing=timing_status
            )

            db.session.add(courier)
            order_id += 1

        # Move to next month
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)

    # Commit all changes
    db.session.commit()
    print("Seeding courier completed successfully!")



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
        seed_products() 
        seed_data()
        seed_user()
        seed_missing_data()
        seed_courier_data()
        seed_orders()
    print("Database setup and seeding complete!")
