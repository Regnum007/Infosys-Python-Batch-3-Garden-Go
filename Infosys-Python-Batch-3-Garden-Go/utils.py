from flask import session, redirect, url_for, flash, request, jsonify
from functools import wraps
from datetime import datetime, timedelta

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'Admin':
            flash("Admin access required.", "alert")
            return redirect(url_for('logint1.login'))
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
       
        if 'user_id' not in session or session.get('role') != 'Customer':
            flash("You need to log in as a customer to access this page.", "danger")
            
           
            return redirect(url_for('logint1.login')) 
            
        return f(*args, **kwargs)
    return decorated_function

def logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            if session.get('role') == 'Admin':
                return redirect(url_for('admint2.admin_home'))

            if session.get('role') == 'Courier':
                return redirect(url_for('couriert3.home'))

            if session.get('role') == 'Customer':
                return redirect(url_for('customert2.product_list'))
        return f(*args, **kwargs)
    return decorated_function


def track_activity(app):
    @app.before_request
    def check_session_timeout():
        if "user_id" in session:
            now = datetime.now()
            last_activity = session.get("last_activity")
            if last_activity:
                last_activity_time = datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S")
                if (now - last_activity_time) > timedelta(minutes=15):
                    session.clear()
                    flash('session expired login again', 'alert')
                    if request.is_json:  # Check if the request is an AJAX request
                        return jsonify({"message": "Session expired", "redirect": url_for("logint1.login")}), 401
                    return redirect(url_for("logint1.login"))
            session["last_activity"] = now.strftime("%Y-%m-%d %H:%M:%S")

def cache_control(app):
    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response