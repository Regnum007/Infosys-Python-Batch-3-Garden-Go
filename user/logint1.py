from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from model import User, PasswordResetToken, Address, db,Product
from datetime import datetime, timedelta
from sqlalchemy import desc
from flask_mail import Mail, Message
import random
import string
import pytz


mail = Mail()
IST = pytz.timezone('Asia/Kolkata')

logint1 = Blueprint("logint1", __name__, static_folder="static", template_folder="templates")

@logint1.route('/')
def index():
    products= Product.query.all()
    return render_template('index.html',products=products)
@logint1.route("/about")
def about():
    return render_template('about.html')
@logint1.route('/address')
def address():
    user = User.query.get_or_404(session['user_id'])
    addresses = Address.query.filter_by(user_id=session['user_id']).all()
    add_list = [f"{a.street_address}, {a.locality}, {a.city}, {a.postal_code}" for a in addresses]
    return render_template('addresses.html', addresses=add_list, user=user)

@logint1.route('/add-address', methods=['POST', 'GET'])
def add_address():
    if request.method == 'GET':
        return render_template('add_address.html')
    elif request.method == 'POST':
        new_add = Address(
            user_id=session['user_id'],
            street_address=request.form['street_address'],
            locality=request.form['locality'],
            city=request.form['city'],
            state=request.form['state'],
            postal_code=request.form['postal_code'])
        try:
            db.session.add(new_add)
            db.session.commit()
            flash('Address added successfully.', 'success')
        except:
            flash('Error in adding address', 'alert')
        return redirect(url_for('logint1.address'))


@logint1.route('/request-reset', methods=['GET', 'POST'])
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

@logint1.route('/customer')
def customer():
    if 'user_id' in session:
        user = User.query.get_or_404(session['user_id'])
        return render_template('customer.html', user=user)
    return redirect(url_for('logint1.login'))


@logint1.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        
        return redirect(url_for('logint1.login'))

    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        print(request.form)  # Debugging to check form data in console
        user.name = request.form['name']
        user.email = request.form['email']
        user.phone_number = request.form['mobile']

        existing_email_user = User.query.filter_by(email=request.form['email']).first()
        if existing_email_user and existing_email_user.user_id != user.user_id:
            flash('Email already exists.', 'alert')
            return redirect(url_for('logint1.profile'))

        existing_phone_user = User.query.filter_by(phone_number=request.form['mobile']).first()
        if existing_phone_user and existing_phone_user.user_id != user.user_id:
            flash('Mobile number already exists.', 'alert')
            return redirect(url_for('logint1.profile'))

        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('logint1.profile'))  # Redirect to customer page
        except Exception as e:
            flash('Error updating profile.', 'alert')
            print(str(e))  # Log error for debugging

    return render_template('profile.html', user=user)

@logint1.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))
    user = User.query.get_or_404(session['user_id'])
    if request.method == 'POST':
        current_password = request.form['currentPassword']
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmPassword']
        if not user.check_password(current_password):
            flash('Current password is incorrect', 'alert')
            return redirect(url_for('logint1.change_password'))
        if new_password != confirm_password:
            flash('New password and confirmation do not match', 'alert')
            return redirect(url_for('logint1.change_password'))
        user.set_password(new_password)
        db.session.commit()
        flash('Password reset successful', 'success')
        return redirect(url_for('customert2.product_list'))
    return render_template('change_password.html', user=user)


@logint1.route('/signup', methods=['POST', 'GET'])
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
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.user_id
            session['role'] = user.role  # Store the user's role
            flash(f'Logged in as {user.role}', 'success')
            
            if user.role == 'Admin':
                return render_template("admin_edit.html")  
            elif user.role == 'Customer':
                return redirect(url_for('customert2.product_list'))
            else:
                return "courier"
        
        flash('Invalid credentials', 'alert')
    return redirect(url_for('logint1.login'))


@logint1.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')
