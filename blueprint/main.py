from flask import Flask,Blueprint
from flask_sqlalchemy import SQLAlchemy
from model import db, Product  # Import your db and models
from app import app as blueprint

from cart import cart as cart
from detail import detail as detail
from place import place as place
from order import order as order
from order2 import order2 as order2
from shipping import shipping  as shipping
  # Import blueprint

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webapp.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'inzamul123'

    db.init_app(app)

    # Register the blueprint
    app.register_blueprint(blueprint,url_prefix='/products')
    
    app.register_blueprint(cart, url_prefix='/cart')
    app.register_blueprint(detail,url_prefix='/detail')
    app.register_blueprint(shipping,url_prefix='/shipping')
    app.register_blueprint(place, url_prefix='/place')
    app.register_blueprint(order, url_prefix='/order')
    app.register_blueprint(order2, url_prefix='/order2')


    # Create tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
