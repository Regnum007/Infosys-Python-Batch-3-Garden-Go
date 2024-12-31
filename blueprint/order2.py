from flask import Blueprint, render_template,redirect,url_for
from model import Product

order2 = Blueprint("order2", __name__, static_folder="static", template_folder="templates")
@order2.route("/order/<int:order_id>")
def order_detail(order_id):
    order = order2.query.get_or_404(order_id)
    return render_template("order_detail.html", order=order)
