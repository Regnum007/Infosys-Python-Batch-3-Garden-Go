from flask import Blueprint, render_template, request,session,redirect,url_for
from model import Product

app = Blueprint("app", __name__, static_folder="static", template_folder="templates")

@app.route("/")
@app.route("/products", methods=["GET"])
def product_list():
    query = request.args.get("query", "").lower()
    products = Product.query.all()

    filtered_products = [
        product for product in products
        if query in product.name.lower()
        or query in product.category_name.lower()
        or query in str(product.selling_price).lower()
        or query in str(product.weight).lower()
    ]

    return render_template("products.html", products=filtered_products if query else products)

        


@app.route("/category/<category>")
def filter_category(category):
    products = Product.query.filter_by(category_name=category).all()
    return render_template("products.html", products=products)

