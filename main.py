from flask import Flask,Blueprint
from flask_sqlalchemy import SQLAlchemy


from model import db
from admin.admint2 import admint2 as admint2
from customer.customert2 import customert2 as customert2
from user.logint1 import logint1 as logint1


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webapp.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'inzamul123'

    db.init_app(app)
    app.register_blueprint(customert2,url_prefix ='/products')
    app.register_blueprint(logint1)
    app.register_blueprint(admint2)
    


   
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)