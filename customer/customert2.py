<<<<<<< HEAD
from flask import Blueprint, render_template, request, session, redirect, url_for, flash,jsonify
from model import Product, User, db, Order,OrderDetail,Cart,Address,Sub,Sales,Buy
from datetime import datetime
import re  
import uuid
from utils import customer_required
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
    sort = request.args.get("sort", "default")
    products = Product.query.all()
    user = None
    ordered_products = []
    if 'user_id' not in session:
        return redirect(url_for('logint1.login')) 

    # Retrieve user if logged in
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user_id = user.user_id
        if user and user.email:
            subscribed = Sub.query.filter_by(email=user.email).first() is not None
    
        # Fetch the most recent order for the user
        recent_order = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).first()
        if recent_order:
            # Get products from the recent order
            order_details = OrderDetail.query.filter_by(order_id=recent_order.order_id).all()
            ordered_products = [Product.query.get(detail.product_id) for detail in order_details]

    # Apply search filtering
    filtered_products = [
        product for product in products
        if query in product.name.lower()
        or query in product.category_name.lower()
        or query in str(product.selling_price).lower()
        or query in str(product.weight).lower()
    ]

    # Sort products based on the 'sort' parameter
    if sort != "default":
        if query:
            if sort == "price_asc":
                filtered_products.sort(key=lambda p: p.selling_price)
            elif sort == "price_desc":
                filtered_products.sort(key=lambda p: p.selling_price, reverse=True)
            elif sort == "weight_asc":
                filtered_products.sort(key=lambda p: p.weight)
            elif sort == "weight_desc":
                filtered_products.sort(key=lambda p: p.weight, reverse=True)
            elif sort == "name_asc":
                filtered_products.sort(key=lambda p: p.name.lower())
            elif sort == "name_desc":
                filtered_products.sort(key=lambda p: p.name.lower(), reverse=True)
        else:
            # If no query, sort the original products list
            if sort == "price_asc":
                products.sort(key=lambda p: p.selling_price)
            elif sort == "price_desc":
                products.sort(key=lambda p: p.selling_price, reverse=True)
            elif sort == "weight_asc":
                products.sort(key=lambda p: p.weight)
            elif sort == "weight_desc":
                products.sort(key=lambda p: p.weight, reverse=True)
            elif sort == "name_asc":
                products.sort(key=lambda p: p.name.lower())
            elif sort == "name_desc":
                products.sort(key=lambda p: p.name.lower(), reverse=True)

    # Render the products page with filtered and sorted products
    return render_template(
        "products.html",
        user=user,
        products=filtered_products if query else products,
        ordered_products=ordered_products,
        sort=sort
    )

@customert2.route("/product/<int:id>")
def product_detail(id):
    product = Product.query.get_or_404(id)
    user = None
    
    total_price = product.selling_price
    if 'user_id' not in session:
        return redirect(url_for('logint1.login')) 
      

    
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)

    
    
    other_products = Product.query.filter(Product.product_id != id).all()

    return render_template(
        "product_detail.html",
        product=product,
        user=user,
        total_price=total_price,
        
        other_products=other_products
    )

@customert2.route("/category/<category>")
def filter_category(category):
   
    selected_category_products = Product.query.filter_by(category_name=category).all()
    
   
    other_category_products = Product.query.filter(Product.category_name != category).all()
    
    return render_template(
        "category.html", 
        products=selected_category_products, 
        other_products=other_category_products
    )


@customert2.route('/set_location', methods=['POST'])
def set_location():
    state = request.form['state']
    postal_code = request.form['postal_code']
    
    
    session['state'] = state
    session['postal_code'] = postal_code

    return redirect(request.referrer)  

@customert2.route('/subscribe', methods=['POST'])
def subscribe():
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))

    user = User.query.get(session['user_id'])
    if not user or not user.email:
        flash("No email associated with your account!", "danger")
        return redirect(url_for('customert2.product_list'))

    email = user.email

    try:
        existing_subscriber = Sub.query.filter_by(email=email).first()
        if existing_subscriber:
            # Unsubscribe logic
            db.session.delete(existing_subscriber)
            db.session.commit()
            flash("Unsubscribed successfully!", "success")
            subscribed = False
        else:
            # Subscribe logic
            new_subscriber = Sub(email=email)
            db.session.add(new_subscriber)
            db.session.commit()
            flash("Subscribed successfully!", "success")
            subscribed = True

        # Pass the subscription status to the template
        return redirect(url_for('customert2.product_list', subscribed=subscribed))

    except Exception as e:
        flash("An error occurred while updating your subscription.", "danger")
        return redirect(url_for('customert2.product_list'))


@customert2.route("/categorycustomer/<category>")
def filter_categorycustomer(category):
    user_id = session.get('user_id')
    other_category_products = Product.query.filter(Product.category_name != category).all()

    if category == 'All':
        selected_category_products = Product.query.all()
    else:
        selected_category_products = Product.query.filter_by(category_name=category).all()

    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    
    if not user_id:
        return redirect(url_for('logint1.login'))
    
    products = selected_category_products
    return render_template("products.html", user=user, products=products, 
                           other_products=other_category_products) 


@customert2.route('/buy')
def buy_cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logint1.login'))

    user = User.query.get(user_id)

    # Fetch all addresses and find the default address
    all_addresses = Address.query.filter_by(user_id=user_id).all()
    default_address = next((address for address in all_addresses if address.default_address), None)

    # Fetch the latest cart item for the user (ensuring only one item at a time)
    buy_items = Buy.query.filter_by(user_id=user_id).order_by(Buy.Buy_id.desc()).first()

    if not buy_items:
        return render_template('buy.html', buy=[], user=user, 
                               default_address=default_address, all_addresses=all_addresses,
                               total_price=0, total_weight=0, shipping_cost=0, 
                               grand_total=0, free_shipping=False, buy_empty=True)

    # Calculate total price and weight (only one item in the cart)
    total_price = buy_items.product.selling_price * buy_items.quantity
    total_weight = buy_items.product.weight * buy_items.quantity

    # Shipping cost logic
    shipping_cost = 29  # Default shipping cost
    state = session.get('state')
    postal_code = session.get('postal_code')

    if state and postal_code:
        try:
            postal_code = int(postal_code)  # Ensure it's an integer
            if state in calculate_states:
                zip_range = calculate_states[state]
                if zip_range[0] <= postal_code <= zip_range[1]:
                    shipping_cost = 0  # Free shipping
                else:
                    shipping_cost = 29  # Standard shipping
            else:
                shipping_cost = 29  # Default shipping cost
        except ValueError:
            shipping_cost = 29  # Default shipping cost

    # Additional logic for weight and price-based shipping cost
    if total_price > 700 or total_weight > 900:
        shipping_cost = 40

    # Calculate grand total
    grand_total = total_price + shipping_cost  # Adding shipping cost to grand total

    # If free shipping, set grand_total to just total_price
    if shipping_cost == 0:
        grand_total = total_price

    return render_template(
        'buy.html',
        buy=[buy_items],  # Only one product in the cart
        user=user,
        default_address=default_address,  
        all_addresses=all_addresses,
        total_price=total_price,
        total_weight=total_weight,
        shipping_cost=shipping_cost,
        free_shipping=(shipping_cost == 0),
        grand_total=grand_total,
        cart_empty=False
    )


@customert2.route('/cart')
def view_cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logint1.login'))

    user = User.query.get(user_id)

    # Fetch all addresses and find the default address
    all_addresses = Address.query.filter_by(user_id=user_id).all()
    default_address = next((address for address in all_addresses if address.default_address), None)

    # Fetch the cart items for the user
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    if not cart_items:
        return render_template('cart.html', cart=cart_items, user=user, 
                               default_address=default_address, all_addresses=all_addresses,
                               total_price=0, total_weight=0, shipping_cost=0, 
                               grand_total=0, free_shipping=False, cart_empty=True)

    # Calculate total price and weight
    total_price = sum(item.product.selling_price * item.quantity for item in cart_items)
    total_weight = sum(item.product.weight * item.quantity for item in cart_items)

    # Shipping cost logic
    shipping_cost = 29  # Default shipping cost
    state = session.get('state')
    postal_code = session.get('postal_code')

    if state and postal_code:
        try:
            postal_code = int(postal_code)  # Ensure it's an integer
            if state in calculate_states:
                zip_range = calculate_states[state]
                if zip_range[0] <= postal_code <= zip_range[1]:
                    shipping_cost = 0  # Free shipping
                else:
                    shipping_cost = 29  # Standard shipping
            else:
                shipping_cost = 29  # Default shipping cost
        except ValueError:
            shipping_cost = 29  # Default shipping cost

    # Additional logic for weight and price-based shipping cost
    if total_price > 700 or total_weight > 900:
        shipping_cost = 40

    # Calculate grand total
    grand_total = total_price + shipping_cost  # Adding shipping cost to grand total

    # If free shipping, set grand_total to just total_price
    if shipping_cost == 0:
        grand_total = total_price

    return render_template(
        'cart.html',
        cart=cart_items,
        user=user,
        default_address=default_address,  # Pass default address to template
        all_addresses=all_addresses,
        total_price=total_price,
        total_weight=total_weight,
        shipping_cost=shipping_cost,
        free_shipping=(shipping_cost == 0),
        grand_total=grand_total,
        cart_empty=False
    )

#direct add to cart
@customert2.route('/direct_add_to_cart/<int:product_id>', methods=['GET'])
def direct_add_to_cart(product_id):
    user_id = session.get('user_id')
    if not user_id:
        
        return redirect(url_for('logint1.login'))
    
    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
    
    db.session.commit()
    
    return redirect(url_for('customert2.product_list'))


# add to cart
@customert2.route('/add_to_cart/<int:product_id>', methods=['GET'])
def add_to_cart(product_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logint1.login'))

    # Query the product and cart
    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()

    # Redirect to the product detail page with the product_id
    return redirect(url_for('customert2.product_detail', id=product_id))




# buy now
@customert2.route('/buy_now/<int:product_id>', methods=['GET'])
def buy_now(product_id):
    user_id = session.get('user_id')
    if not user_id:
        
        return redirect(url_for('logint1.login'))
    
    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
    
    db.session.commit()
    
    return redirect(url_for('customert2.view_cart'))

@customert2.route('/buy_nows/<int:product_id>', methods=['GET'])
def buy_nows(product_id):
    user_id = session.get('user_id')
    if not user_id:
        
        return redirect(url_for('logint1.login'))
    
    product = Product.query.get_or_404(product_id)
    buy_items = Buy.query.filter_by(user_id=user_id, product_id=product_id).first()

    if buy_items:
        buy_items.quantity += 1
    else:
        buy_items = Buy(user_id=user_id, product_id=product_id, quantity=1)
        db.session.add(buy_items)
    
    db.session.commit()
    
    return redirect(url_for('customert2.buy_cart'))

# Remove from Cart
@customert2.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    user_id = session.get('user_id')
    user = None
    if not user_id:
        return redirect(url_for('customert2.view_cart'))

    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    
    return redirect(url_for('customert2.view_cart',user=user))

@customert2.route('/remove_from_buy/<int:product_id>', methods=['POST'])
def remove_from_buy(product_id):
    user_id = session.get('user_id')
    user = None
    if not user_id:
        return redirect(url_for('customert2.buy_cart'))

    buy_items = Buy.query.filter_by(user_id=user_id, product_id=product_id).first()
    if buy_items:
        db.session.delete(buy_items)
        db.session.commit()
    
    return redirect(url_for('customert2.buy_cart',user=user))


# Delete Cart
@customert2.route('/delete_cart', methods=['POST'])
def delete_cart():
    user_id = session.get('user_id')
    if user_id:
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
    return redirect(url_for('customert2.view_cart'))



@customert2.route('/get_cart_data', methods=['GET'])
def get_cart_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 400

    cart_items = Cart.query.filter_by(user_id=user_id).all()
    
   
    total_quantity = sum(item.quantity for item in cart_items)
    total_weight = sum(item.product.weight * item.quantity for item in cart_items)

   
    cart_data = {
        'cart_items': [
            {
                'product_id': item.product_id,
                'name': item.product.name,
                'quantity': item.quantity,
                'weight': item.product.weight,
                'sub_total': item.product.selling_price * item.quantity
            }
            for item in cart_items
        ],
        'total_quantity': total_quantity,
        'total_weight': total_weight
    }

    return jsonify(cart_data)



@customert2.route('/increment_quantity/<int:product_id>', methods=['POST'])
def increment_quantity(product_id):
    user_id = session.get('user_id')  
    
    
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1  
        db.session.commit()  
    else:
       
        pass

    
    return redirect(url_for('customert2.view_cart'))

@customert2.route('/increment_quantitybuy/<int:product_id>', methods=['POST'])
def increment_quantitybuy(product_id):
    user_id = session.get('user_id')  
    
    
    buy_items = Buy.query.filter_by(user_id=user_id, product_id=product_id).first()

    if buy_items:
        buy_items.quantity += 1  
        db.session.commit()  
    else:
       
        pass

    
    return redirect(url_for('customert2.buy_cart'))


@customert2.route('/decrement_quantity/<int:product_id>', methods=['POST'])
def decrement_quantity(product_id):
    user_id = session.get('user_id') 
    
    
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  
        else:
            db.session.delete(cart_item)  
        db.session.commit()  
    else:
        
        pass

    
    return redirect(url_for('customert2.view_cart'))
# Decrement quantity in the cart
@customert2.route('/decrement_quantitybuy/<int:product_id>', methods=['POST'])
def decrement_quantitybuy(product_id):
    user_id = session.get('user_id') 
    
    
    buy_items = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if buy_items:
        if buy_items.quantity > 1:
            buy_items.quantity -= 1  
        else:
            db.session.delete(buy_items)  
        db.session.commit()  
    else:
        
        pass

    
    return redirect(url_for('customert2.buy_cart'))



@customert2.route('/order_confirmation_cart')
def order_confirmation_cart():
    user = None
    order = Order.query.filter_by(user_id=session.get('user_id')).order_by(Order.created_at.desc()).first()

    if not order:
        return redirect(url_for('customert2.product_list'))

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user_id = user.user_id

    order_details = OrderDetail.query.filter_by(order_id=order.order_id).all()

    ordered_products = []
    for detail in order_details:
        product = Product.query.get(detail.product_id)
        sub_total = detail.sub_Total
        
        ordered_products.append({
            'product': product,
            'quantity': detail.quantity,
            'sub_total': sub_total
        })
        
        # Insert into Sales table
        revenue = sub_total  # Assuming revenue = total price of sold units
        cost_price = product.cost_price if hasattr(product, 'cost_price') else 0
        profit = revenue - (cost_price * detail.quantity)  

        new_sale = Sales(
            product_id=product.product_id,
            units_sold=detail.quantity,
            revenue=revenue,
            profit=profit,
            sales_date=datetime.utcnow(),
        )
        db.session.add(new_sale)

    # Calculate total price and weight
    total_price = sum(item['sub_total'] for item in ordered_products)
    total_weight = sum(item['product'].weight * item['quantity'] for item in ordered_products)

    shipping_cost = order.shipping_cost  
    shipping_cost_from_request = request.args.get('shippingCost')  

    if shipping_cost_from_request:
        shipping_cost = re.sub(r'[^0-9.]', '', shipping_cost_from_request)
        shipping_cost = float(shipping_cost)

    grand_total = total_price + shipping_cost

    confirmed_address = Address.query.filter_by(user_id=user_id).order_by(Address.created_at.desc()).first()

    # Commit the sales data to the database
    db.session.commit()

    return render_template(
        'order_confirmation.html',
        order=order,
        user=user,
        user_id=user_id,
        ordered_products=ordered_products,
        message="Your order has been confirmed.",
        grand_total=grand_total,
        shipping_cost=shipping_cost,
        total_weight=total_weight,
        confirmed_address=confirmed_address  
    )


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
    query = request.args.get("query", "").lower()
    products = Product.query.all()
    user=None
    user_id = session.get('user_id')
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user_id = user.user_id

    filtered_products = [
        product for product in products
        if query in product.name.lower()
        or query in product.category_name.lower()
        or query in str(product.selling_price).lower()
        or query in str(product.weight).lower()
    ]
    if not user_id:
        return redirect(url_for('customert2.product_list'))
    
    
    orders = Order.query.filter_by(user_id=user_id).all()
    
    order_details = []
    
   
    for order in orders:
        details = OrderDetail.query.filter_by(order_id=order.order_id).all()
        order_details.append({
            'order': order,
            'details': details
        })
    
    return render_template('order_history.html', order_details=order_details,user=user,user_id=user_id,products=filtered_products if query else products)




@customert2.route("/buy_now_from_buy", methods=["POST"])
@customer_required
def buy_now_from_buy():
    user_id = session.get('user_id')
    shipping_cost = request.form.get('shippingCost')
      
    
    if shipping_cost:
        
        numeric_shipping_cost = re.sub(r'[^\d.]+', '', shipping_cost)
        try:
            shipping_cost = float(numeric_shipping_cost) 
        except ValueError:
            shipping_cost = 0.0  

   
    buy_items = Buy.query.filter_by(user_id=user_id).all()
    if not buy_items:
        return redirect(url_for('customert2.buy_cart'))
    total_price = sum(item.product.selling_price * item.quantity for item in buy_items)
    total_weight = sum(item.product.weight * item.quantity for item in buy_items)

 
    grand_total = total_price + shipping_cost

    
    order = Order(
        order_id=str(uuid.uuid4()),
        user_id=user_id,
        total_price=grand_total,
        shipping_cost=shipping_cost,
        status="Pending",
        created_at=datetime.utcnow(),
        quantities=len(buy_items),
        prices=total_price
    )
    db.session.add(order)
    db.session.commit()

 
    for item in buy_items:
        order_detail = OrderDetail(
            order_id=order.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            sub_Total=item.product.selling_price * item.quantity
        )
        db.session.add(order_detail)

   
    try:
        Buy.query.filter_by(user_id=user_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing cart: {str(e)}")

   
    return redirect(url_for('customert2.order_confirmation_cart', order_id=order.order_id, shippingCost=shipping_cost))

# Buy Now

@customert2.route("/buy_now_from_cart", methods=["POST"])
@customer_required
def buy_now_from_cart():
    user_id = session.get('user_id')
    shipping_cost = request.form.get('shippingCost')
      
    
    if shipping_cost:
        
        numeric_shipping_cost = re.sub(r'[^\d.]+', '', shipping_cost)
        try:
            shipping_cost = float(numeric_shipping_cost) 
        except ValueError:
            shipping_cost = 0.0  

   
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return redirect(url_for('customert2.view_cart'))
    total_price = sum(item.product.selling_price * item.quantity for item in cart_items)
    total_weight = sum(item.product.weight * item.quantity for item in cart_items)

 
    grand_total = total_price + shipping_cost

    
    order = Order(
        order_id=str(uuid.uuid4()),
        user_id=user_id,
        total_price=grand_total,
        shipping_cost=shipping_cost,
        status="Pending",
        created_at=datetime.utcnow(),
        quantities=len(cart_items),
        prices=total_price
    )
    db.session.add(order)
    db.session.commit()

 
    for item in cart_items:
        order_detail = OrderDetail(
            order_id=order.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            sub_Total=item.product.selling_price * item.quantity
        )
        db.session.add(order_detail)

   
    try:
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing cart: {str(e)}")

   
    return redirect(url_for('customert2.order_confirmation_cart', order_id=order.order_id, shippingCost=shipping_cost))

@customert2.route('/add_shipping_address', methods=['POST'])
def add_shipping_address():
    # Get the form data
    street_address = request.form.get('street_address')
    locality = request.form.get('locality')
    city = request.form.get('city')
    state = request.form.get('state')
    postal_code = request.form.get('postal_code')
    user_id = session.get("user_id")
    
    # Check if any required fields are missing
    if not all([street_address, locality, city, state, postal_code]):
        flash("Please fill in all the required fields.", "danger")
        return redirect(url_for('customert2.view_cart'))

    # Convert 'on' to True and everything else to False for default_address
    default_address = True if request.form.get('default_address') == 'on' else False

    try:
        # Save the new address to the database
        new_address = Address(
            user_id=user_id,
            street_address=street_address,
            locality=locality,
            city=city,
            state=state,
            postal_code=postal_code,
            default_address=default_address  # Set the default address flag
        )

        # If the new address is set as default, make sure to unset other default addresses for the user
        if default_address:
            # Update existing addresses to ensure only one default
            Address.query.filter_by(user_id=user_id).update({"default_address": False})
        
        db.session.add(new_address)
        db.session.commit()

        # Optionally, save the state and postal code to the session (if needed for other parts of the application)
        session['state'] = state
        session['postal_code'] = postal_code

        # Provide success message to the user
        flash("Shipping address added successfully!", "success")
        
        # Redirect to the view_cart page
        return redirect(url_for('customert2.view_cart'))
    
    except Exception as e:
        # Handle any potential errors during database operations
        db.session.rollback()  # Rollback in case of any error
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('customert2.view_cart'))

@customert2.route('/faqs')
def faqs():
    return render_template('faqs.html')
=======
from flask import Blueprint, render_template, request, session, redirect, url_for, flash,jsonify
from model import Product, User, db, Order,OrderDetail,Cart,Address,Sub,Sales,Buy
from datetime import datetime
import re  
import uuid
from utils import customer_required
customert2 = Blueprint("customert2", __name__, static_folder="static", template_folder="templates")

calculate_states = {
    "Delhi": [110001, 110099],
    "delhi": [110001, 110099],
}

free_states = ["Goa", "Maharashtra", "Karnataka"]

# Product List
@customert2.route("/", methods=["GET", "POST"])
def product_list():
    query = request.args.get("query", "").lower()
    sort = request.args.get("sort", "default")
    products = products = Product.query.filter_by(is_deleted=False).all() 
    user = None
    ordered_products = []

    if 'user_id' not in session:
        return redirect(url_for('logint1.login')) 

    # Retrieve user if logged in
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user_id = user.user_id
        if user and user.email:
            # Check if the user is subscribed
            subscribed = Sub.query.filter_by(email=user.email).first() is not None

        # Fetch the most recent order for the user
        recent_order = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).first()
        if recent_order:
            # Get products from the recent order
            order_details = OrderDetail.query.filter_by(order_id=recent_order.order_id).all()
            ordered_products = [Product.query.get(detail.product_id) for detail in order_details]

    # Handle subscription toggle if the form is submitted
    if request.method == "POST" and user:
        if 'subscribe' in request.form:
            # Add subscription logic
            if not subscribed:
                new_subscription = Sub(email=user.email)
                db.session.add(new_subscription)
                db.session.commit()
                subscribed = True
        elif 'unsubscribe' in request.form:
            # Remove subscription logic
            existing_subscription = Sub.query.filter_by(email=user.email).first()
            if existing_subscription:
                db.session.delete(existing_subscription)
                db.session.commit()
                subscribed = False

    # Apply search filtering
    filtered_products = [
        product for product in products
        if query in product.name.lower()
        or query in product.category_name.lower()
        or query in str(product.selling_price).lower()
        or query in str(product.weight).lower()
    ]

    # Sort products based on the 'sort' parameter
    if sort != "default":
        if query:
            if sort == "price_asc":
                filtered_products.sort(key=lambda p: p.selling_price)
            elif sort == "price_desc":
                filtered_products.sort(key=lambda p: p.selling_price, reverse=True)
            elif sort == "weight_asc":
                filtered_products.sort(key=lambda p: p.weight)
            elif sort == "weight_desc":
                filtered_products.sort(key=lambda p: p.weight, reverse=True)
            elif sort == "name_asc":
                filtered_products.sort(key=lambda p: p.name.lower())
            elif sort == "name_desc":
                filtered_products.sort(key=lambda p: p.name.lower(), reverse=True)
        else:
            # If no query, sort the original products list
            if sort == "price_asc":
                products.sort(key=lambda p: p.selling_price)
            elif sort == "price_desc":
                products.sort(key=lambda p: p.selling_price, reverse=True)
            elif sort == "weight_asc":
                products.sort(key=lambda p: p.weight)
            elif sort == "weight_desc":
                products.sort(key=lambda p: p.weight, reverse=True)
            elif sort == "name_asc":
                products.sort(key=lambda p: p.name.lower())
            elif sort == "name_desc":
                products.sort(key=lambda p: p.name.lower(), reverse=True)

    # Render the products page with filtered and sorted products
    return render_template(
        "products.html",
        user=user,
        products=filtered_products if query else products,
        ordered_products=ordered_products,
        sort=sort,
        subscribed=subscribed  # Pass the subscription status to the template
    )


@customert2.route("/product/<int:id>")
def product_detail(id):
    product = Product.query.get_or_404(id)
    user = None
    
    total_price = product.selling_price
    if 'user_id' not in session:
        return redirect(url_for('logint1.login')) 
      

    
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)

    
    
    other_products = Product.query.filter(Product.product_id != id, Product.is_deleted == False).all()


    return render_template(
        "product_detail.html",
        product=product,
        user=user,
        total_price=total_price,
        
        other_products=other_products
    )

@customert2.route("/category/<category>")
def filter_category(category):
   
    if category == 'All':
        selected_category_products = Product.query.filter_by(is_deleted=False).all()
    else:
        selected_category_products = Product.query.filter_by(category_name=category, is_deleted=False).all()
    
   
    other_category_products = Product.query.filter(Product.category_name != category, Product.is_deleted == False).all()
    
    return render_template(
        "category.html", 
        products=selected_category_products, 
        other_products=other_category_products
    )


@customert2.route('/set_location', methods=['POST'])
def set_location():
    state = request.form['state']
    postal_code = request.form['postal_code']
    
    
    session['state'] = state
    session['postal_code'] = postal_code

    return redirect(request.referrer)  

@customert2.route('/subscribe', methods=['POST'])
def subscribe():
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))

    user = User.query.get(session['user_id'])
    if not user or not user.email:
        flash("No email associated with your account!", "danger")
        return redirect(url_for('customert2.product_list'))

    email = user.email

    try:
        existing_subscriber = Sub.query.filter_by(email=email).first()
        if existing_subscriber:
            # Unsubscribe logic
            db.session.delete(existing_subscriber)
            db.session.commit()
            flash("Unsubscribed successfully!", "success")
            subscribed = False
        else:
            # Subscribe logic
            new_subscriber = Sub(email=email)
            db.session.add(new_subscriber)
            db.session.commit()
            flash("Subscribed successfully!", "success")
            subscribed = True

        # Pass the subscription status to the template
        return redirect(url_for('customert2.product_list', subscribed=subscribed))

    except Exception as e:
        flash("An error occurred while updating your subscription.", "danger")
        return redirect(url_for('customert2.product_list'))


@customert2.route("/categorycustomer/<category>")
def filter_categorycustomer(category):
    user_id = session.get('user_id')

    # Fetch only non-deleted products that are NOT in the selected category
    other_category_products = Product.query.filter(Product.category_name != category, Product.is_deleted == False).all()

    # Fetch selected category products, ensuring they are not deleted
    if category == 'All':
        selected_category_products = Product.query.filter_by(is_deleted=False).all()
    else:
        selected_category_products = Product.query.filter_by(category_name=category, is_deleted=False).all()

    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

    if not user_id:
        return redirect(url_for('logint1.login'))

    products = selected_category_products
    return render_template(
        "products.html", 
        user=user, 
        products=products, 
        other_products=other_category_products
    )

@customert2.route('/buy')
def buy_cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logint1.login'))

    user = User.query.get(user_id)

    # Fetch all addresses and find the default address
    all_addresses = Address.query.filter_by(user_id=user_id).all()
    default_address = next((address for address in all_addresses if address.default_address), None)

    # Fetch the latest Buy item (ensuring only one item at a time)
    buy_item = Buy.query.filter_by(user_id=user_id).order_by(Buy.Buy_id.desc()).first()

    if not buy_item:
        return render_template('buy.html', buy=[], user=user, 
                               default_address=default_address, all_addresses=all_addresses,
                               total_price=0, total_weight=0, shipping_cost=0, 
                               grand_total=0, free_shipping=False, buy_empty=True)

    # Calculate total price and weight (only one item)
    total_price = buy_item.product.selling_price * buy_item.quantity
    total_weight = buy_item.product.weight * buy_item.quantity

    # Shipping cost logic
    shipping_cost = 29  # Default shipping cost
    state = session.get('state')
    postal_code = session.get('postal_code')

    if state and postal_code:
        try:
            postal_code = int(postal_code)  # Ensure it's an integer
            if state in calculate_states:
                zip_range = calculate_states[state]
                if zip_range[0] <= postal_code <= zip_range[1]:
                    shipping_cost = 0  # Free shipping
                else:
                    shipping_cost = 29  # Standard shipping
            else:
                shipping_cost = 29  # Default shipping cost
        except ValueError:
            shipping_cost = 29  # Default shipping cost

    # Additional logic for weight and price-based shipping cost
    if total_price > 700 or total_weight > 900:
        shipping_cost = 40

    # Calculate grand total
    grand_total = total_price + shipping_cost  
    if shipping_cost == 0:
        grand_total = total_price  # Free shipping case

    return render_template(
        'buy.html',
        buy=[buy_item],  # Only one product
        user=user,
        default_address=default_address,  
        all_addresses=all_addresses,
        total_price=total_price,
        total_weight=total_weight,
        shipping_cost=shipping_cost,
        free_shipping=(shipping_cost == 0),
        grand_total=grand_total,
        cart_empty=False
    )


@customert2.route('/cart')
def view_cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logint1.login'))

    user = User.query.get(user_id)

    # Fetch addresses
    all_addresses = Address.query.filter_by(user_id=user_id).all()
    default_address = next((address for address in all_addresses if address.default_address), None)

    # Fetch all cart items
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    if not cart_items:
        return render_template('cart.html', cart=[], user=user, 
                               default_address=default_address, all_addresses=all_addresses,
                               total_price=0, total_weight=0, shipping_cost=0, 
                               grand_total=0, free_shipping=False, cart_empty=True)

    # Calculate total price and weight
    total_price = sum(item.product.selling_price * item.quantity for item in cart_items)
    total_weight = sum(item.product.weight * item.quantity for item in cart_items)

    # Shipping cost logic
    shipping_cost = 29  
    state = session.get('state')
    postal_code = session.get('postal_code')

    if state and postal_code:
        try:
            postal_code = int(postal_code)  
            if state in calculate_states:
                zip_range = calculate_states[state]
                if zip_range[0] <= postal_code <= zip_range[1]:
                    shipping_cost = 0  
                else:
                    shipping_cost = 29  
            else:
                shipping_cost = 29  
        except ValueError:
            shipping_cost = 29  

    # Additional weight and price-based shipping cost
    if total_price > 700 or total_weight > 900:
        shipping_cost = 40

    # Calculate grand total
    grand_total = total_price + shipping_cost  
    if shipping_cost == 0:
        grand_total = total_price  

    return render_template(
        'cart.html',
        cart=cart_items,
        user=user,
        default_address=default_address,  
        all_addresses=all_addresses,
        total_price=total_price,
        total_weight=total_weight,
        shipping_cost=shipping_cost,
        free_shipping=(shipping_cost == 0),
        grand_total=grand_total,
        cart_empty=False
    )


# Add to Cart (Preserves Future Checkout Items)
@customert2.route('/add_to_cart/<int:product_id>', methods=['GET'])
def add_to_cart(product_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logint1.login'))

    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash("Product added to cart!", "success")
    return redirect(url_for('customert2.product_detail', id=product_id))

@customert2.route('/direct_add_to_cart/<int:product_id>', methods=['GET'])
def direct_add_to_cart(product_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logint1.login'))

    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash("Product added to cart!", "success")
    return redirect(url_for('customert2.product_list', id=product_id))


# Buy Now (Handles Single Product Checkout Separately)
@customert2.route('/buy_now/<int:product_id>', methods=['GET'])
def buy_now(product_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logint1.login'))

    product = Product.query.get_or_404(product_id)

    # Remove previous Buy items to ensure only one product for Buy Now
    Buy.query.filter_by(user_id=user_id).delete()
    
    buy_item = Buy(user_id=user_id, product_id=product_id, quantity=1)
    db.session.add(buy_item)
    
    db.session.commit()
    return redirect(url_for('customert2.buy_cart'))


# Remove from Cart
@customert2.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    user_id = session.get('user_id')
    user = None
    if not user_id:
        return redirect(url_for('customert2.view_cart'))

    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    
    return redirect(url_for('customert2.view_cart',user=user))

@customert2.route('/remove_from_buy/<int:product_id>', methods=['POST'])
def remove_from_buy(product_id):
    user_id = session.get('user_id')
    user = None
    if not user_id:
        return redirect(url_for('customert2.buy_cart'))

    buy_items = Buy.query.filter_by(user_id=user_id, product_id=product_id).first()
    if buy_items:
        db.session.delete(buy_items)
        db.session.commit()
    
    return redirect(url_for('customert2.buy_cart',user=user))


# Delete Cart
@customert2.route('/delete_cart', methods=['POST'])
def delete_cart():
    user_id = session.get('user_id')
    if user_id:
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
    return redirect(url_for('customert2.view_cart'))



@customert2.route('/get_cart_data', methods=['GET'])
def get_cart_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 400

    cart_items = Cart.query.filter_by(user_id=user_id).all()
    
   
    total_quantity = sum(item.quantity for item in cart_items)
    total_weight = sum(item.product.weight * item.quantity for item in cart_items)

   
    cart_data = {
        'cart_items': [
            {
                'product_id': item.product_id,
                'name': item.product.name,
                'quantity': item.quantity,
                'weight': item.product.weight,
                'sub_total': item.product.selling_price * item.quantity
            }
            for item in cart_items
        ],
        'total_quantity': total_quantity,
        'total_weight': total_weight
    }

    return jsonify(cart_data)



@customert2.route('/increment_quantity/<int:product_id>', methods=['POST'])
def increment_quantity(product_id):
    user_id = session.get('user_id')  
    
    
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1  
        db.session.commit()  
    else:
       
        pass

    
    return redirect(url_for('customert2.view_cart'))

@customert2.route('/increment_quantitybuy/<int:product_id>', methods=['POST'])
def increment_quantitybuy(product_id):
    user_id = session.get('user_id')  
    
    
    buy_items = Buy.query.filter_by(user_id=user_id, product_id=product_id).first()

    if buy_items:
        buy_items.quantity += 1  
        db.session.commit()  
    else:
       
        pass

    
    return redirect(url_for('customert2.buy_cart'))


@customert2.route('/decrement_quantity/<int:product_id>', methods=['POST'])
def decrement_quantity(product_id):
    user_id = session.get('user_id') 
    
    
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  
        else:
            db.session.delete(cart_item)  
        db.session.commit()  
    else:
        
        pass

    
    return redirect(url_for('customert2.view_cart'))
# Decrement quantity in the cart
@customert2.route('/decrement_quantitybuy/<int:product_id>', methods=['POST'])
def decrement_quantitybuy(product_id):
    user_id = session.get('user_id') 
    
    
    buy_items = Buy.query.filter_by(user_id=user_id, product_id=product_id).first()

    if buy_items:
        if buy_items.quantity > 1:
            buy_items.quantity -= 1  
        else:
            db.session.delete(buy_items)  
        db.session.commit()  
    else:
        
        pass

    
    return redirect(url_for('customert2.buy_cart'))



@customert2.route('/order_confirmation_cart')
def order_confirmation_cart():
    user = None
    order = Order.query.filter_by(user_id=session.get('user_id')).order_by(Order.created_at.desc()).first()

    if not order:
        return redirect(url_for('customert2.product_list'))

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user_id = user.user_id

    order_details = OrderDetail.query.filter_by(order_id=order.order_id).all()

    ordered_products = []
    for detail in order_details:
        product = Product.query.get(detail.product_id)
        sub_total = detail.sub_Total
        
        ordered_products.append({
            'product': product,
            'quantity': detail.quantity,
            'sub_total': sub_total
        })
        
        # Insert into Sales table
        revenue = sub_total  # Assuming revenue = total price of sold units
        cost_price = product.cost_price if hasattr(product, 'cost_price') else 0
        profit = revenue - (cost_price * detail.quantity)  

        new_sale = Sales(
            product_id=product.product_id,
            units_sold=detail.quantity,
            revenue=revenue,
            profit=profit,
            sales_date=datetime.utcnow(),
        )
        db.session.add(new_sale)

    # Calculate total price and weight
    total_price = sum(item['sub_total'] for item in ordered_products)
    total_weight = sum(item['product'].weight * item['quantity'] for item in ordered_products)

    shipping_cost = order.shipping_cost  
    shipping_cost_from_request = request.args.get('shippingCost')  

    if shipping_cost_from_request:
        shipping_cost = re.sub(r'[^0-9.]', '', shipping_cost_from_request)
        shipping_cost = float(shipping_cost)

    grand_total = total_price + shipping_cost

    confirmed_address = Address.query.filter_by(user_id=user_id).order_by(Address.created_at.desc()).first()

    # Commit the sales data to the database
    db.session.commit()

    return render_template(
        'order_confirmation.html',
        order=order,
        user=user,
        user_id=user_id,
        ordered_products=ordered_products,
        message="Your order has been confirmed.",
        grand_total=grand_total,
        shipping_cost=shipping_cost,
        total_weight=total_weight,
        confirmed_address=confirmed_address  
    )


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
    query = request.args.get("query", "").lower()
    products = Product.query.all()
    user=None
    user_id = session.get('user_id')
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user_id = user.user_id

    filtered_products = [
        product for product in products
        if query in product.name.lower()
        or query in product.category_name.lower()
        or query in str(product.selling_price).lower()
        or query in str(product.weight).lower()
    ]
    if not user_id:
        return redirect(url_for('customert2.product_list'))
    
    
    orders = Order.query.filter_by(user_id=user_id).all()
    
    order_details = []
    
   
    for order in orders:
        details = OrderDetail.query.filter_by(order_id=order.order_id).all()
        order_details.append({
            'order': order,
            'details': details
        })
    
    return render_template('order_history.html', order_details=order_details,user=user,user_id=user_id,products=filtered_products if query else products)




@customert2.route("/buy_now_from_buy", methods=["POST"])
@customer_required
def buy_now_from_buy():
    user_id = session.get('user_id')
    shipping_cost = request.form.get('shippingCost')
      
    
    if shipping_cost:
        
        numeric_shipping_cost = re.sub(r'[^\d.]+', '', shipping_cost)
        try:
            shipping_cost = float(numeric_shipping_cost) 
        except ValueError:
            shipping_cost = 0.0  

   
    buy_items = Buy.query.filter_by(user_id=user_id).all()
    if not buy_items:
        return redirect(url_for('customert2.buy_cart'))
    total_price = sum(item.product.selling_price * item.quantity for item in buy_items)
    total_weight = sum(item.product.weight * item.quantity for item in buy_items)

 
    grand_total = total_price + shipping_cost

    
    order = Order(
        order_id=str(uuid.uuid4()),
        user_id=user_id,
        total_price=grand_total,
        shipping_cost=shipping_cost,
        status="Pending",
        created_at=datetime.utcnow(),
        quantities=len(buy_items),
        prices=total_price
    )
    db.session.add(order)
    db.session.commit()

 
    for item in buy_items:
        order_detail = OrderDetail(
            order_id=order.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            sub_Total=item.product.selling_price * item.quantity
        )
        db.session.add(order_detail)

   
    try:
        Buy.query.filter_by(user_id=user_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing cart: {str(e)}")

   
    return redirect(url_for('customert2.order_confirmation_cart', order_id=order.order_id, shippingCost=shipping_cost))

# Buy Now

@customert2.route("/buy_now_from_cart", methods=["POST"])
@customer_required
def buy_now_from_cart():
    user_id = session.get('user_id')
    shipping_cost = request.form.get('shippingCost')
      
    
    if shipping_cost:
        
        numeric_shipping_cost = re.sub(r'[^\d.]+', '', shipping_cost)
        try:
            shipping_cost = float(numeric_shipping_cost) 
        except ValueError:
            shipping_cost = 0.0  

   
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return redirect(url_for('customert2.view_cart'))
    total_price = sum(item.product.selling_price * item.quantity for item in cart_items)
    total_weight = sum(item.product.weight * item.quantity for item in cart_items)

 
    grand_total = total_price + shipping_cost

    
    order = Order(
        order_id=str(uuid.uuid4()),
        user_id=user_id,
        total_price=grand_total,
        shipping_cost=shipping_cost,
        status="Pending",
        created_at=datetime.utcnow(),
        quantities=len(cart_items),
        prices=total_price
    )
    db.session.add(order)
    db.session.commit()

 
    for item in cart_items:
        order_detail = OrderDetail(
            order_id=order.order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            sub_Total=item.product.selling_price * item.quantity
        )
        db.session.add(order_detail)

   
    try:
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing cart: {str(e)}")

   
    return redirect(url_for('customert2.order_confirmation_cart', order_id=order.order_id, shippingCost=shipping_cost))

@customert2.route('/add_shipping_address', methods=['POST'])
def add_shipping_address():
    street_address = request.form.get('street_address')
    locality = request.form.get('locality')
    city = request.form.get('city')
    state = request.form.get('state')
    postal_code = request.form.get('postal_code')
    next_url = request.form.get("next_url")  
    user_id = session.get("user_id")

   
    if not all([street_address, locality, city, state, postal_code]):
        flash("Please fill in all the required fields.", "danger")
        return redirect(next_url or url_for('customert2.view_cart'))  

    
    default_address = True if request.form.get('default_address') == 'on' else False

    try:
       
        new_address = Address(
            user_id=user_id,
            street_address=street_address,
            locality=locality,
            city=city,
            state=state,
            postal_code=postal_code,
            default_address=default_address
        )

       
        if default_address:
            Address.query.filter_by(user_id=user_id).update({"default_address": False})
        
        db.session.add(new_address)
        db.session.commit()

      
        session['state'] = state
        session['postal_code'] = postal_code

        flash("Shipping address added successfully!", "success")
        
        
        return redirect(next_url or url_for('customert2.view_cart'))
    
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(next_url or url_for('customert2.view_cart'))
  
    except Exception as e:
       
        db.session.rollback()  
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('customert2.view_cart'))

@customert2.route('/faqs')
def faqs():
    return render_template('faqs.html')
>>>>>>> 29a49f9 (Updated files)
