from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from model import Product, User, db, Order,OrderDetail
from datetime import datetime
import uuid
from util import customer_required 
customert2 = Blueprint("customert2", __name__, static_folder="static", template_folder="templates")

calculate_states = {
    "Delhi": [110001, 110099],
    "delhi": [110001, 110099],
}

free_states = ["Goa", "Maharashtra", "Karnataka"]

# Product List
@customert2.route("/", methods=["GET"])
def product_list():
    query = request.args.get("query", "").lower()
    products = Product.query.all()
    user = None
    ordered_products = []

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    
        user_id = user.user_id
    
   
        recent_order = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).first()

        if recent_order:
           
            order_details = OrderDetail.query.filter_by(order_id=recent_order.order_id).all()

          
            ordered_products = [Product.query.get(detail.product_id) for detail in order_details]

    filtered_products = [
        product for product in products
        if query in product.name.lower()
        or query in product.category_name.lower()
        or query in str(product.selling_price).lower()
        or query in str(product.weight).lower()
    ]

    return render_template("products.html", user=user, products=filtered_products if query else products, ordered_products=ordered_products)

# Product Detail
@customert2.route("/product/asgdysdgasyudgud<int:id>adgagduadaud")
def product_detail(id):
    product = Product.query.get_or_404(id)
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

    other_products = Product.query.filter(Product.product_id != id).all()

    return render_template(
        "product_detail.html",
        product=product,
        total_price=total_price,
        shipping_cost=shipping_cost,
        free_shipping=shipping_cost == 0,
        other_products=other_products,
    )

@customert2.route("/category/<category>")
def filter_category(category):
    products = Product.query.filter_by(category_name=category).all()
    return render_template("products.html", products=products)

@customert2.route("/set_location", methods=["POST"])
def set_location():
    session['zipcode'] = request.form.get("zipcode")
    session['city'] = request.form.get("city")
    return redirect(url_for("customert2.product_list"))
# Cart View
@customert2.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    total_weight = sum(item['weight'] * item['quantity'] for item in cart)
    shipping_cost = 0 if session.get('city') in calculate_states else 29

    if total_price > 700 or total_weight > 900:
        shipping_cost = 40

    grand_total = total_price + shipping_cost

    return render_template('cart.html',
                           cart=cart,
                           total_price=total_price,
                           shipping_cost=shipping_cost,
                           free_shipping=shipping_cost == 0,
                           grand_total=grand_total)

# Add to Cart
@customert2.route('/add_to_cart/<int:product_id>', methods=['GET'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = session.get('cart', [])
    existing_item = next((item for item in cart if item['product_id'] == product.product_id), None)

    if existing_item:
        existing_item['quantity'] += 1
    else:
        cart.append({
            'product_id': product.product_id,
            'name': product.name,
            'price': product.selling_price,
            'quantity': 1,
            'weight': product.weight,
            'image_url': product.image_url
        })

    session['cart'] = cart
    return redirect(url_for('customert2.view_cart'))

# Remove from Cart
@customert2.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    return redirect(url_for('customert2.view_cart'))

# Delete Cart
@customert2.route('/delete_cart', methods=['POST'])
def delete_cart():
    session.pop('cart', None)
    return redirect(url_for('customert2.view_cart'))

# Checkout
@customert2.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('customert2.view_cart'))

    total_price = sum(item['price'] * item['quantity'] for item in cart)
    total_weight = sum(item['weight'] * item['quantity'] for item in cart)
    shipping_cost = 0 if session.get('city') in calculate_states else 29

    if total_price > 700 or total_weight > 900:
        shipping_cost = 40

    grand_total = total_price + shipping_cost

    user_id = session.get('user_id')

  
    new_order = Order(
        order_id=str(uuid.uuid4()), 
        user_id=user_id,
        total_price=grand_total,
        shipping_cost=shipping_cost,
        status="Pending",
        created_at=datetime.utcnow(),
        quantities=sum(item['quantity'] for item in cart), 
        prices=total_price,  
    )
    
    db.session.add(new_order)

    
    for item in cart:
        order_detail = OrderDetail(
            order_id=new_order.order_id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            sub_Total=item['price'] * item['quantity']
        )
        db.session.add(order_detail)

    db.session.commit()

    session.pop('cart', None)

    flash("Order placed successfully!", "success")
    return redirect(url_for('customert2.order_confirmation_cart'))

# Increment Quantity
@customert2.route('/increment_quantity/<int:product_id>', methods=['POST'])
def increment_quantity(product_id):
    cart = session.get('cart', [])
    
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += 1
            break
    
    session['cart'] = cart
    return redirect(url_for('customert2.view_cart'))

# Decrement Quantity
@customert2.route('/decrement_quantity/<int:product_id>', methods=['POST'])
def decrement_quantity(product_id):
    cart = session.get('cart', [])
    
    for item in cart:
        if item['product_id'] == product_id:
            if item['quantity'] > 1:
                item['quantity'] -= 1
            else:
                cart = [i for i in cart if i['product_id'] != product_id]
            break
    
    session['cart'] = cart
    return redirect(url_for('customert2.view_cart'))

# Order Confirmation
@customert2.route('/order_confirmation_cart')
def order_confirmation_cart():
   
    
    order = Order.query.filter_by(user_id=session.get('user_id')).order_by(Order.created_at.desc()).first()
    if order:
        
       
        return render_template('order_confirmation.html', order=order, message="Your order has been confirmed.")
    else:
        flash("No orders found.", "danger")
        return redirect(url_for('customert2.product_list'))


# Order Detail
@customert2.route("/order/<int:order_id>")
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    order_details = OrderDetail.query.filter_by(order_id=order.order_id).all()
    
    products_in_order = []
    for detail in order_details:
        product = Product.query.get(detail.product_id)
        products_in_order.append({
            'product': product,
            'quantity': detail.quantity,
            'sub_total': detail.sub_Total
        })
    
    return render_template("order_detail.html", order=order, products_in_order=products_in_order)

# Order History
@customert2.route('/order_history')
def order_history():
    user_id = session.get('user_id')
    if not user_id:
        flash("You need to log in to view your orders.", "warning")
        return redirect(url_for('customert2.product_list'))
    
    
    orders = Order.query.filter_by(user_id=user_id).all()
    
    order_details = []
    
   
    for order in orders:
        details = OrderDetail.query.filter_by(order_id=order.order_id).all()
        order_details.append({
            'order': order,
            'details': details
        })
    
    return render_template('order_history.html', order_details=order_details)

# Buy Now
@customert2.route("/buy_now/<int:product_id>", methods=["GET", "POST"])
@customer_required
def buy_now(product_id):
    product = Product.query.get_or_404(product_id)
    shipping_cost = 29
    total_price = product.selling_price
    zipcode = session.get("zipcode")
    city = session.get("city")

    if zipcode and city and city in calculate_states:
        zip_range = calculate_states[city]
        if zip_range[0] <= int(zipcode) <= zip_range[1]:
            shipping_cost = 0
    total_price += shipping_cost

    
    user_id = session.get('user_id')

    order = Order(
        order_id=str(uuid.uuid4()),
        user_id=user_id,
        total_price=total_price,
        shipping_cost=shipping_cost,
        status="Pending",
        created_at=datetime.utcnow(),
        quantities=1,  
        prices=product.selling_price
    )
    
    db.session.add(order)

    
    order_detail = OrderDetail(
        order_id=order.order_id,
        product_id=product.product_id,
        quantity=1,
        sub_Total=product.selling_price
    )
    db.session.add(order_detail)

    db.session.commit()

    return redirect(url_for('customert2.order_confirmation_cart', order_id=order.order_id))