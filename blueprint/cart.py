from flask import Blueprint, render_template, request,session,redirect,url_for
from model import Product

cart = Blueprint("cart", __name__, static_folder="static", template_folder="templates")

calculate_states = {
    "Delhi": [110001, 110099],
    
}
free_states = ["Goa", "Maharashtra", "Karnataka"]

@cart.route('/cart')
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

@cart.route("/set_location", methods=["POST"])
def set_location():
    session['zipcode'] = request.form.get("zipcode")
    session['city'] = request.form.get("city")
    return redirect(url_for("app.product_list"))

@cart.route('/add_to_cart/<int:product_id>', methods=['GET'])
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
            'weight':product.weight,
            'image_url': product.image_url
        })

    session['cart'] = cart
    return redirect(url_for('cart.view_cart'))

@cart.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    return redirect(url_for('cart.view_cart'))

@cart.route('/delete_cart', methods=['POST'])
def delete_cart():
    session.pop('cart', None)
    return redirect(url_for('cart.view_cart'))

@cart.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    
    if not cart:
        return redirect(url_for('cart.view_cart'))

   
    for item in cart:
        print(f"Processing {item['name']} - Quantity: {item['quantity']} - Price: {item['price']} ") 

   
    session.pop('cart', None)
    
    return redirect(url_for('order.order_confirmation_cart'))

@cart.route('/increment_quantity/<int:product_id>', methods=['POST'])
def increment_quantity(product_id):
    cart = session.get('cart', [])
    
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += 1
            break
    
    session['cart'] = cart
    return redirect(url_for('cart.view_cart'))

@cart.route('/decrement_quantity/<int:product_id>', methods=['POST'])
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
    return redirect(url_for('cart.view_cart'))