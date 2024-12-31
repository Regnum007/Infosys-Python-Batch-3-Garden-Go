from flask import Blueprint, render_template,redirect,url_for
from model import Product

order = Blueprint("order", __name__, static_folder="static", template_folder="templates")
@order.route('/order_confirmation_cart')
def order_confirmation_cart():
    return render_template('order_confirmation.html')
