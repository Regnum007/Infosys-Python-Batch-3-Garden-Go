from flask import Blueprint, request, redirect, url_for, render_template, flash
from model import Product,User,db
from utils import admin_required  
import os

admint2 = Blueprint(
    "admint2", 
    __name__, 
    static_folder="../static",  
    template_folder="templates"
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admint2.route("/admin/edit")
@admin_required
def edit_product():
    return render_template("admin_edit.html")


@admint2.route('/admin/edit/modify', methods=['GET', 'POST'])
@admin_required
def modify_products():
    products = Product.query.all()
    selected_product = None

    if request.method == 'POST':
        product_name = request.form.get('product_name')
        
        if product_name:
            selected_product = Product.query.filter_by(name=product_name).first()
            
            if not selected_product:
                flash('Selected product not found.', 'danger')
                return redirect(url_for('admint2.modify_products'))

            selected_product.name = request.form.get('name', selected_product.name)
            selected_product.category_name = request.form.get('category_name', selected_product.category_name)
            selected_product.description = request.form.get('description', selected_product.description)
            selected_product.weight = request.form.get('weight', selected_product.weight)
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
