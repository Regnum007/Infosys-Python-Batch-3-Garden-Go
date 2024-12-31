from flask import Blueprint, render_template, request,session
from model import Product

shipping = Blueprint("shipping", __name__, static_folder="static", template_folder="templates")

calculate_states = {
    "Delhi": [110001, 110099],
    
}
free_states = ["Goa", "Maharashtra", "Karnataka"]

@shipping.route("/buy_now/<int:product_id>", methods=["GET", "POST"])
def buy_now(product_id):
    product = Product.query.get_or_404(product_id)
    zipcode = session.get("zipcode")
    city = session.get("city")
    shipping_cost = 29
    total_price = product.selling_price

    if zipcode and city:
        if city in calculate_states:
            zip_range = calculate_states[city]
            if zip_range[0] <= int(zipcode) <= zip_range[1]:
                shipping_cost = 0
        total_price += shipping_cost

    return render_template(
        "buy_now.html",
        product=product,
        total_price=total_price,
        shipping_cost=shipping_cost,
        free_shipping=shipping_cost == 29,
    )