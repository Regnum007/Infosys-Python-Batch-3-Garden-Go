from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app
from model import Product, User, db, IST
from utils import admin_required
from sqlalchemy import or_, desc
from datetime import datetime, timedelta
from flask_mail import Message
import plotly.graph_objs as go
import plotly.io as pio
import sys
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if base_dir not in sys.path:
    sys.path.append(base_dir)
from user.logint1 import mail


admint2 = Blueprint(
    "admint2", 
    __name__, 
    static_folder="../static",  
    template_folder="templates"
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admint2.route("/admin/home")
@admin_required
def admin_home():
    return render_template("admin.html")

@admint2.route("/admin/category")
def filteradmin_category(category):
    products = Product.query.filter_by(category_name=category).all()
    return render_template("products.html", products=products)


@admint2.route("/admin/edit")
@admin_required
def edit_product():
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

    return render_template(
        "admin_edit.html",
        products=filtered_products if query else products,
        ordered_products=ordered_products,
        sort=sort
    )
  

@admint2.route('/admin/edit/modify', methods=['GET', 'POST'])
@admin_required
def modify_products():
<<<<<<< HEAD
    products = Product.query.all()
=======
    # Fetch only non-deleted products
    products = Product.query.filter_by(is_deleted=False).all()
>>>>>>> 29a49f9 (Updated files)
    selected_product = None

    if request.method == 'POST':
        product_name = request.form.get('product_name')
<<<<<<< HEAD
        
        if product_name:
            selected_product = Product.query.filter_by(name=product_name).first()
            
            if not selected_product:
                flash('Selected product not found.', 'danger')
=======

        if product_name:
            selected_product = Product.query.filter_by(name=product_name, is_deleted=False).first()
            
            if not selected_product:
                flash('Selected product not found or has been deleted.', 'danger')
>>>>>>> 29a49f9 (Updated files)
                return redirect(url_for('admint2.modify_products'))

            selected_product.name = request.form.get('name', selected_product.name)
            selected_product.category_name = request.form.get('category_name', selected_product.category_name)
            selected_product.description = request.form.get('description', selected_product.description)
            selected_product.weight = request.form.get('weight', selected_product.weight)
            selected_product.selling_price = request.form.get('cost_price', selected_product.cost_price)
            selected_product.selling_price = request.form.get('selling_price', selected_product.selling_price)
            
            image_url = request.form.get('image_url')
            if image_url and allowed_file(image_url):
                selected_product.image_url = image_url

            db.session.commit()
            flash('Product modified successfully.', 'success')
            return redirect(url_for('admint2.modify_products'))
        else:
            flash('Please select a product to modify.', 'warning')

    return render_template('modify.html', products=products)


@admint2.route('/admin/edit/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category_name = request.form['category_name']
        cost_price = float(request.form['cost_price'])
        selling_price = float(request.form['selling_price'])
        weight = request.form['weight']
        stock_quantity = request.form['stock_quantity']
        
        image_url = request.form.get('image_url')
        uploaded_file = request.files.get('image_file')

        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = uploaded_file.filename
            file_path = os.path.join(admint2.static_folder, filename)
            os.makedirs(admint2.static_folder, exist_ok=True)
            uploaded_file.save(file_path)
            image_path = filename  
        elif image_url and allowed_file(image_url):
            image_path = image_url
        else:
            image_path = 'default.png'

        new_product = Product(
            name=name,
            description=description,
            category_name=category_name,
            cost_price=cost_price,
            selling_price=selling_price,
            image_url=image_path,
            weight=weight,
            stock_quantity=stock_quantity
        )
        db.session.add(new_product)
        db.session.commit()

        flash('Product added successfully.', 'success')
        return redirect(url_for('admint2.edit_product'))

    return render_template('add_product.html')


@admint2.route('/admin/edit/delete', methods=['GET', 'POST'])
@admin_required
def delete_products():
    products = Product.query.filter_by(is_deleted=False).all()
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        product = Product.query.get(product_id)
        
        if product:
            product.is_deleted = True
            db.session.commit()
            flash('Product deleted successfully.', 'danger')
        else:
            flash('Product not found.', 'warning')
        
        return redirect(url_for('admint2.delete_products'))

    return render_template('delete.html', products=products)


@admint2.route('/admin/edit/recover', methods=['GET', 'POST'])
@admin_required
def recovery_products():
    deleted_products = Product.query.filter_by(is_deleted=True).all()
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        action = request.form.get('action')
        product = Product.query.get(product_id)
        
        if product:
            if action == 'recover':
                product.is_deleted = False
                db.session.commit()
                flash('Product recovered successfully.', 'success')
            elif action == 'delete':
                db.session.delete(product)
                db.session.commit()
                flash('Product permanently deleted.', 'danger')
        else:
            flash('Product not found.', 'warning')
        
        return redirect(url_for('admint2.recovery_products'))

    return render_template('recover.html', products=deleted_products)


@admint2.route('/admin/manage-users', methods=['GET', 'POST'])
@admin_required
def manage_users():
    if request.method == 'GET':
        users = User.query.order_by(desc(User.is_active)).all()
        search_query = request.args.get('search', '').lower()
        page = request.args.get('page', 1, type=int)
        per_page = 10

        # Filter users based on the search query
        if search_query:
            filtered_users = db.session.query(User).filter(
                or_(
                    User.email.ilike("%"+search_query+"%"),  # Case-insensitive match for email
                    User.phone_number.like("%"+search_query+"%")  # Case-sensitive match for mobile number
                )
            ).order_by(desc(User.is_active)).all()
        else:
            filtered_users = users
        # Pagination logic
        total_users = len(filtered_users)
        total_pages = (total_users + per_page - 1) // per_page  # Ceiling division
        start = (page - 1) * per_page
        end = start + per_page
        paginated_users = filtered_users[start:end]
        return render_template('manage_users.html', users=users, paginated_users=paginated_users, current_page=page, total_pages=total_pages,search_query=search_query)


@admint2.route('/admin/view-user/<int:user_id>', methods=['POST'])
@admin_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('view_user.html', user=user)


@admint2.route('/admin/deactivate/<int:user_id>', methods=['POST'])
@admin_required
def deactivate(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    flash(f' user ID {user_id}\'s account has been Deactivated.', 'success')
    return redirect(url_for('admint2.manage_users'))
@admint2.route('/admin/reactivation-requests', methods=['GET', 'POST'])
@admin_required
def reactivation_requests():
    requests = User.query.filter_by(account_request=1).order_by(desc(User.last_login)).all()
    return render_template('reactivation_approval.html', requests=requests)



@admint2.route('/admin/approve-request/<int:user_id>', methods=['POST'])
@admin_required
def approve_request(user_id):
    user = User.query.get_or_404(user_id)
    user.account_request = 0
    user.is_active = 1
    db.session.commit()

    # Send approval email
    msg = Message(
        'Reactivation request',
        recipients=[user.email],
        html=(
            f'<h3>Hello {user.name},</h3>'
            f'<p>Your reactivation request for the Garden Go Auto Courier Connect account has been approved.</p>'
            f'<p>You can access the account <a href="{url_for("logint1.index", _external=True)}">Here</a></p>'
        )
    )
    mail.send(msg)

    flash(f'Reactivation request for user ID {user_id} has been approved.', 'success')
    return redirect(url_for('admint2.reactivation_requests'))


@admint2.route('/admin/reject-request/<int:user_id>', methods=['POST'])
@admin_required
def reject_request(user_id):
    user = User.query.get_or_404(user_id)
    user.account_request = 0
    db.session.commit()

    # Send rejection email
    msg = Message(
        'Reactivation request',
        recipients=[user.email],
        html=(
            f'<h3>Hello {user.name},</h3>'
            f'<p>Your reactivation request for the Garden Go Auto Courier Connect account has been rejected.</p>'
            f'<p>You can make another request by visiting '
            f'<a href="{url_for("logint1.reactivation", user_id=user.id, _external=True)}">Here</a>.</p>'
        )
    )
    mail.send(msg)

    flash(f'Reactivation request for user ID {user_id} has been rejected.', 'danger')
    return redirect(url_for('admint2.reactivation_requests'))


@admint2.route('/admin/admin_stats')
def active_sessions():
    session_model = current_app.session_interface.sql_session_model

    # Query for active sessions
    active_sessions_count = db.session.query(session_model).filter(
        session_model.expiry > datetime.utcnow()
    ).count()
    total_user_count = User.query.count()
    reactivation_count = User.query.filter_by(account_request=1).count()

    return {
        "active_sessions": active_sessions_count,
        "total_users": total_user_count,
        "reactivation_count": reactivation_count
    }


@admint2.route('/admin/user_plot')
def generate_user_registration_plot():
    now = datetime.now(IST)
    months = []
    for i in range(12):
        first_day_of_month = (now - timedelta(days=1)).replace(day=1)
        months.append(first_day_of_month)
        now = first_day_of_month
    months.reverse()


    # Query the database for user counts
    user_counts = []
    for i in range(len(months) - 1):
        count = User.query.filter(User.created_at >= months[i], User.created_at < months[i + 1]).count()
        user_counts.append(count)
    # Add current month's users
    user_counts.append(User.query.filter(User.created_at >= months[-1]).count())
    month_labels = [month.strftime("%b %Y") for month in months]
    bar_chart = go.Bar(
        x=month_labels,
        y=user_counts,
        marker=dict(color='skyblue'),
        hoverinfo='x+y',  # Show both month and count on hover
        text=user_counts,  # Text to display above bars
        textposition='auto'
    )
    layout = go.Layout(
        title='User Registrations Over the Past 12 Months',
        xaxis=dict(title='Month', tickangle=-45),
        yaxis=dict(title='Number of Users'),
        bargap=0.2
    )
    fig = go.Figure(data=[bar_chart], layout=layout)
    config = {
        'displayModeBar': False,  # Disable the mode bar
    }
    plot_html = pio.to_html(fig, full_html=False, config=config)
    return {"plot_html": plot_html}



