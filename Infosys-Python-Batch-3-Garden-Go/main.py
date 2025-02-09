from flask import Flask,Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_session import Session
from utils import track_activity, cache_control
from model import db

from admin.admint2 import admint2 as admint2
from couriert3.couriert3 import couriert3 as couriert3
from customer.customert2 import customert2 as customert2
from analyst.analystt4 import analystt4 as analystt4
from user.logint1 import logint1 as logint1, mail


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webapp.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'inzamul123'

    db.init_app(app)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'test.smtp.send1@gmail.com'
    app.config['MAIL_PASSWORD'] = 'boih ltuk fdxo lcrv'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_DEFAULT_SENDER'] = ('Garden Go Auto Courier Connect', 'test.smtp.send1@gmail.com')
    mail.init_app(app)

    app.config["SESSION_TYPE"] = "sqlalchemy"
    app.config["SESSION_PERMANENT"] = True
    app.config["SESSION_USE_SIGNER"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)
    app.config["SESSION_SQLALCHEMY"] = db
    Session(app)
    app.register_blueprint(customert2,url_prefix ='/products')
    app.register_blueprint(logint1)
    app.register_blueprint(admint2)
    app.register_blueprint(couriert3)
    app.register_blueprint(analystt4)
    
    track_activity(app)
    cache_control(app)
   
    with app.app_context():
        db.create_all()


    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
