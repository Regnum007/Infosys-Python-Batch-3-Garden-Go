from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify,make_response
from model import User, PasswordResetToken, Address, db, Product
from datetime import datetime, timedelta
from sqlalchemy import desc
from flask_mail import Mail, Message
import random
import string
import pytz
from utils import logged_in

mail = Mail()
IST = pytz.timezone('Asia/Kolkata')

logint1 = Blueprint("logint1", __name__, static_folder="static", template_folder="templates")


@logint1.route('/')
@logged_in
def index():
    query = request.args.get("query", "").lower()
    sort = request.args.get("sort", "default")
<<<<<<< HEAD
    products = Product.query.all()
=======
    products = products = Product.query.filter_by(is_deleted=False).all() 
>>>>>>> 29a49f9 (Updated files)
    
    ordered_products = []
    
    # Apply search filtering
    filtered_products = [
        product for product in products
        if query in product.name.lower()
        or query in product.category_name.lower()
        or query in str(product.selling_price).lower()
        or query in str(product.weight).lower()
    ]

    return render_template(
        "index.html",
        products=filtered_products if query else products,
        ordered_products=ordered_products,
        sort=sort
    )

   
@logint1.route('/productdetail/<int:id>')
@logged_in
def indexproduct(id):
    product = Product.query.get_or_404(id)
<<<<<<< HEAD
    other_products = Product.query.filter(Product.product_id != id).all()
=======
    other_products = Product.query.filter(Product.product_id != id, Product.is_deleted == False).all()
>>>>>>> 29a49f9 (Updated files)

    return render_template('indexpeoduct.html',other_products=other_products, product=product)


@logint1.route("/about")
def about():
    user=None
    
      

    
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
    return render_template('about.html',user=user)


@logint1.route('/address')
def address():
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))
    user = User.query.get_or_404(session['user_id'])
    addresses = Address.query.filter_by(user_id=session['user_id']).all()
    add_list = [
        {"id": a.address_id, "full_address": f"{a.street_address}, {a.locality}, {a.city}, {a.postal_code}", "default_address": a.default_address}
        for a in addresses
    ]

    return render_template('addresses.html', addresses=add_list, user=user)


@logint1.route('/add-address', methods=['POST', 'GET'])
def add_address():
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'GET':
        return render_template('add_address.html', user=user)
    elif request.method == 'POST':
        saved_add = Address.query.filter_by(user_id=session['user_id']).all()
        new_add = Address(
            user_id=session['user_id'],
            street_address=request.form['street_address'],
            locality=request.form['locality'],
            city=request.form['city'],
            state=request.form['state'],
            postal_code=request.form['postal_code'],
            default_address=True if not saved_add else False)

        try:
            db.session.add(new_add)
            db.session.commit()
            flash('Address added successfully.', 'success')
        except:
            flash('Error in adding address', 'alert')
        return redirect(url_for('logint1.address'))



@logint1.route('/address/update/<string:address_id>', methods=['GET','POST'])
def update_address(address_id):
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))

    # Retrieve the address
    address = Address.query.filter_by(address_id=address_id).first_or_404()

    # Ensure the logged-in user owns the address
    if address.user_id != session['user_id']:
        return "Unauthorized", 403

    # Retrieve the user details
    user = User.query.filter_by(user_id=session['user_id']).first()

    if request.method == 'POST':
        # Update the address fields with the new values from the form
        address.street_address = request.form['street_address']
        address.locality = request.form['locality']
        address.city = request.form['city']
        address.state = request.form['state']
        address.postal_code = request.form['postal_code']

        # Commit the changes to the database
        db.session.commit()

        flash('Address updated successfully!', 'success')
        return redirect(url_for('logint1.address'))

    # Render the update address form and pass the 'user' to the template
    return render_template('add_address.html', address=address, user=user)



@logint1.route('/address/delete/<string:address_id>', methods=['POST'])
def delete_address(address_id):
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))

    # Retrieve the address
    address = Address.query.filter_by(address_id=address_id).first_or_404()

    # Ensure the logged-in user owns the address
    if address.user_id != session['user_id']:
        return "Unauthorized", 403

    db.session.delete(address)
    db.session.commit()
    flash('Address deleted successfully!', 'success')
    return redirect(url_for('logint1.address'))


@logint1.route('/address/set_default/<int:address_id>', methods=['POST'])
def set_default_address(address_id):
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))

    # Get the address to be set as default
    address = Address.query.get_or_404(address_id)

    # Ensure the address belongs to the logged-in user
    if address.user_id != session['user_id']:
        return "Unauthorized", 403

    # Reset all other addresses for the user to not default
    Address.query.filter_by(user_id=session['user_id'], default_address=True).update({"default_address": False})

    # Set the current address as default
    address.default_address = True
    db.session.commit()

    flash('Default address updated successfully!', 'success')
    return redirect(url_for('logint1.address'))


@logint1.route('/request-reset', methods=['GET', 'POST'])
@logged_in
def request_reset():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash('Email not registered', 'alert')
            return redirect(url_for('logint1.request_reset'))

        otp = ''.join(random.choices(string.digits, k=6))
        token = PasswordResetToken(
            token=otp, user=user, created_at=datetime.now(IST),
            expires_at=datetime.now(IST) + timedelta(minutes=15))

        db.session.add(token)
        db.session.commit()
        msg = Message('Reset Your Password', recipients=[email], body=f'Your OTP: {otp}')
        mail.send(msg)
        flash('OTP sent to email.', 'success')
        session['email_verification'] = email
        return redirect(url_for('logint1.verify_otp'))
    return render_template('request_reset.html')


@logint1.route('/verify-otp', methods=['GET', 'POST'])
@logged_in
def verify_otp():
    if 'email_verification' in session:
        if request.method == 'POST':
            otp = request.form['otp']
            new_password = request.form['new_password']
            email = session['email_verification']
            user = User.query.filter_by(email=email).first()
            token = PasswordResetToken.query.filter_by(user_id=user.user_id).order_by(desc(PasswordResetToken.token_id)).first()

            if token.token != otp:
                flash(f'Invalid OTP', 'alert')
                return redirect(url_for('logint1.verify_otp'))
            elif token.expires_at <= datetime.now(IST).replace(tzinfo=None):
                flash('Expired OTP', 'alert')
                return redirect(url_for('logint1.request_reset'))
            else:
                user.set_password(new_password)
                db.session.commit()
                flash('Password reset successful.', 'success')
                return redirect(url_for('logint1.login'))
        return render_template('verify_otp.html')
    return redirect(url_for('logint1.login'))


@logint1.route('/profile', methods=['GET', 'POST'])
def profile():
    # Ensure the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))

    # Fetch the current user from the database
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        # Update user details from form inputs
        user.name = request.form['name']
        user.email = request.form['email']
        user.phone_number = request.form['mobile']

        # Check if the email already exists for another user
        existing_email_user = User.query.filter_by(email=request.form['email']).first()
        if existing_email_user and existing_email_user.user_id != user.user_id:
            flash('Email already exists.', 'alert')
            return redirect(url_for('logint1.profile'))

        # Check if the phone number already exists for another user
        existing_phone_user = User.query.filter_by(phone_number=request.form['mobile']).first()
        if existing_phone_user and existing_phone_user.user_id != user.user_id:
            flash('Mobile number already exists.', 'alert')
            return redirect(url_for('logint1.profile'))

     
        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')

       
            if user.role == 'Admin':
                return redirect(url_for('admint2.admin_home'))
            elif user.role == 'Customer':
                return redirect(url_for('customert2.product_list'))
            elif user.role == 'Courier':
                return redirect(url_for('couriert3.home'))
            else:
                return "courier"
        except Exception as e:
            flash('Error updating profile.', 'alert')
            print(f"Error: {str(e)}")  
  
    return render_template('profile.html', user=user)


@logint1.route('/change-password', methods=['GET', 'POST'])
def change_password():
    # Ensure the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))

    # Fetch the current user from the database
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        # Retrieve form inputs
        current_password = request.form['currentPassword']
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmPassword']

        # Validate current password
        if not user.check_password(current_password):
            flash('Current password is incorrect.', 'alert')
            return redirect(url_for('logint1.change_password'))

        # Check if new password matches confirmation
        if new_password != confirm_password:
            flash('New password and confirmation do not match.', 'alert')
            return redirect(url_for('logint1.change_password'))

       
        try:
            user.set_password(new_password)  
            db.session.commit()
            flash('Password reset successful.', 'success')

           
            if user.role == 'Admin':
                return redirect(url_for('admint2.admin_home'))  
            elif user.role == 'Customer':
                return redirect(url_for('customert2.product_list'))
            else:
                return redirect(url_for('couriert2.courier_dashboard'))  
        except Exception as e:
            flash('An error occurred while updating your password.', 'alert')
            print(f"Error: {str(e)}") 
            return redirect(url_for('logint1.change_password'))


    return render_template('change_password.html', user=user)



@logint1.route('/signup', methods=['POST', 'GET'])
@logged_in
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['mobile']
        password = request.form['password']
        role = request.form['role']
        admin_key = request.form.get('admin-key')

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'alert')
            return redirect(url_for('logint1.signup'))

        new_user = User(
            name=name, email=email, phone_number=phone_number,
            password=password, role=role)

        try:
            if role == 'Admin' and admin_key == 'admin123':
                db.session.add(new_user)
            elif role != 'Admin':
                db.session.add(new_user)
            else:
                flash('Invalid admin key', 'alert')
                return redirect(url_for('logint1.signup'))
            db.session.commit()

            msg = Message('Welcome!', recipients=[new_user.email],
                          body=f'Hello {new_user.name}, welcome to Garden Go Auto Courier Connect!')
            mail.send(msg)

            flash('User registered successfully.', 'success')
            return redirect(url_for('logint1.login'))
        except Exception as e:
            return redirect(url_for('logint1.login'))


@logint1.route('/login', methods=['POST', 'GET'])
@logged_in
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                return redirect(url_for('logint1.reactivation', user_id=user.user_id))
            session['user_id'] = user.user_id
            session['role'] = user.role  
            session['name'] = user.name
            user.last_login = datetime.now(IST)
            db.session.commit()
            flash(f'Logged in as {user.role}', 'success')

            if user.role == 'Admin':
                return redirect(url_for('admint2.admin_home'))
            elif user.role == 'Customer':
                return redirect(url_for('customert2.product_list'))
            elif user.role == 'Courier':
                return redirect(url_for('couriert3.home'))
            else:
                return "None"

        flash('Invalid credentials', 'alert')
    return redirect(url_for('logint1.login'))


@logint1.route('/reactivation', methods=['POST'])
@logint1.route('/reactivation/<user_id>', methods=['GET', 'POST'])
def reactivation(user_id=0):
    if request.method == 'GET':
        user = User.query.get_or_404(user_id)
        if user.account_request:
            return render_template('activation.html', request_exists=1)
        return render_template('activation.html')
    elif request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        # Simulate reactivation logic
        if user and user.check_password(password):  # Add your actual validation here
            # Reactivation request logic (e.g., store request, notify admin)
            user.account_request = True
            db.session.commit()
            return jsonify({"message": "Request received"}), 200
        else:
            return jsonify({"error": "Invalid data"}), 400

@logint1.route('/deactivation-request', methods=['POST', 'GET'])
def deactivation_request():
    if request.method == 'GET':
        user = User.query.get_or_404(session['user_id'])
        return render_template('deactivation_request.html', user=user)
    elif request.method == 'POST':
        user = User.query.get_or_404(session['user_id'])
        password = request.form['password']

        if user and user.check_password(password):
            user.is_active = False
            db.session.commit()
            return redirect(url_for('logint1.logout'))
        else:
            flash('Wrong Password', 'alert')
            return redirect(url_for('logint1.deactivation_request'))

    return redirect(url_for('logint1.login'))


@logint1.route('/logout')
def logout():
    # Clear the session to log the user out
    session.clear()

    # Set cache control headers to prevent the page from being cached
    response = make_response(redirect('/'))  # Redirect to login after logout
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@logint1.route('/update_activity', methods=['POST'])
def update_activity():
    if "user_id" in session:
        return jsonify({"message": "Activity updated"}), 200
    return jsonify({"message": "Session expired"}), 401