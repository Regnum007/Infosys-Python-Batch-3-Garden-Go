from flask import session, redirect, url_for, flash
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'Admin':
            flash("Admin access required.", "danger")
            return redirect(url_for('logint1.login'))
        return f(*args, **kwargs)
    return decorated_function
