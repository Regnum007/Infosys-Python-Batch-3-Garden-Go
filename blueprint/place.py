from flask import Blueprint, render_template,redirect,url_for
from model import Product

place = Blueprint("place", __name__, static_folder="static", template_folder="templates")
@place.route('/place_order/<int:product_id>', methods=['POST'])
def place_order(product_id):
    product = Product.query.get_or_404(product_id)
    
    return redirect(url_for('order.order_confirmation_cart', product_id=product.product_id))
