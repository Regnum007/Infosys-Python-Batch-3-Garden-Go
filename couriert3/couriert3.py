from flask import Flask, render_template, request, redirect, flash, url_for, send_file,Blueprint,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px
import plotly.io as pio
from plotly.graph_objs import Figure, Scatter
from model import Sub,DeliveryIssue,Courier,db,User,Order,OrderDetail
import os

static_folder = os.path.join(os.path.dirname(__file__), 'static')
template_folder = os.path.join(os.path.dirname(__file__), 'templates')

couriert3 = Blueprint("couriert3", __name__, static_folder=static_folder, template_folder=template_folder)
@couriert3.route('/courier', methods=['GET', 'POST'])
def home():
    user = None

    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))

    user = User.query.get(session['user_id']) if 'user_id' in session else None

    # Fetching pending orders
    pending_orders = Order.query.filter_by(status='Pending').all()

    if request.method == 'POST':
        try:
            order_id = request.form['orderid']
            courier_name = request.form['courier_name']
            status = request.form['status']

            # Creating Courier record
            courier = Courier(order_id=order_id, courier_name=courier_name, status=status)
            db.session.add(courier)

            # Updating the Order status
            order = Order.query.get(order_id)
            if order:
                order.status = status  

                # Updating associated OrderDetails
                order_details = OrderDetail.query.filter_by(order_id=order_id).all()
                for detail in order_details:
                    detail.status = status  

            db.session.commit()  
            flash("Order and Order Details updated successfully!", "success")
        except Exception as e:
            db.session.rollback() 
            flash(f"Error: {e}", "danger")
        return redirect(url_for('couriert3.home'))

    # Search and filter logic
    filter_status = request.args.get('filter_status', None)
    search_query = request.args.get('search_query', '').strip()
    todos_query = Courier.query

    if filter_status:
        todos_query = todos_query.filter_by(status=filter_status)
    if search_query:
        todos_query = todos_query.filter(
            (Courier.order_id.like(f"%{search_query}%")) |
            (Courier.courier_name.like(f"%{search_query}%"))
        )

    all_todos = todos_query.all()

    # Date filtering for status counts
    today = datetime.utcnow().date()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    status_counts = {
        "total_orders": Courier.query.count(),
        "today_orders": Courier.query.filter(Courier.date_created >= today).count(),
        "month_orders": Courier.query.filter(Courier.date_created >= start_of_month).count(),
        "year_orders": Courier.query.filter(Courier.date_created >= start_of_year).count(),
        "Dispatched": Courier.query.filter_by(status="Dispatched").count(),
        "In Transit": Courier.query.filter_by(status="In Transit").count(),
        "Out for Delivery": Courier.query.filter_by(status="Out for Delivery").count(),
        "Delivered": Courier.query.filter_by(status="Delivered").count(),
        "Failed Attempt": Courier.query.filter_by(status="Failed Attempt").count(),
    }

    return render_template(
        'dash.html', 
        user=user, 
        allTodo=all_todos, 
        status_counts=status_counts, 
        search_query=search_query, 
        filter_status=filter_status,
        pending_orders=pending_orders,
        courier_name=user.name if user else ''  # Passing the courier name to the template
    )


@couriert3.route('/analytics')
def analytics():
    user = None 

    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))  

    
    user = User.query.get(session['user_id']) if 'user_id' in session else None

    try:
     
        subscribers = Sub.query.all()

     
        if not subscribers:
            return "No subscription data available to generate analytics."

      
        data = [{"id": sub.id, "email": sub.email, "date_created": sub.date_created} for sub in subscribers]
        df = pd.DataFrame(data)

       
        df['date_created'] = pd.to_datetime(df['date_created'], errors='coerce')
        df = df.dropna(subset=['date_created'])  

        if df.empty:
            return "No valid subscription data available."

        
        df['year'] = df['date_created'].dt.year
        df['month'] = df['date_created'].dt.month
        df['day'] = df['date_created'].dt.date

      
        daily_counts = df.groupby('day').size()
        monthly_counts = df.groupby('month').size()
        yearly_counts = df.groupby('year').size()

       
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(20, 10), constrained_layout=True)

        
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.plot(daily_counts.index, daily_counts.values, color='green', marker='o', linestyle='--', linewidth=2)
        ax1.set_title('Subscriptions Per Day', fontsize=14)
        ax1.set_xlabel('Day', fontsize=12)
        ax1.set_ylabel('Count', fontsize=12)
        ax1.grid(color='red', linestyle='--', linewidth=0.5)

       
        ax2 = fig.add_subplot(2, 2, 2, projection='3d')
        years = list(yearly_counts.index)
        counts = list(yearly_counts.values)
        z_values = np.random.uniform(0.5, 1.5, len(counts))
        scatter = ax2.scatter(years, counts, z_values, c=counts, cmap='plasma', s=100, depthshade=True)
        ax2.set_title('Subscriptions Per Year (3D)', fontsize=14)
        ax2.set_xlabel('Year', fontsize=12)
        ax2.set_ylabel('Count', fontsize=12)
        ax2.set_zlabel('Relative Intensity', fontsize=12)
        fig.colorbar(scatter, ax=ax2, shrink=0.6, aspect=10)

     
        ax3 = fig.add_subplot(2, 2, 3)
        colors = plt.cm.viridis(np.linspace(0, 1, len(monthly_counts)))
        ax3.bar(monthly_counts.index, monthly_counts.values, color=colors, edgecolor='red')
        ax3.set_title('Subscriptions Per Month', fontsize=14)
        ax3.set_xlabel('Month', fontsize=12)
        ax3.set_ylabel('Count', fontsize=12)
        ax3.set_xticks(np.arange(1, 13, 1))

      
        ax4 = fig.add_subplot(2, 2, 4)
        explode = [0.1] * len(yearly_counts)
        ax4.pie(
            yearly_counts,
            labels=yearly_counts.index,
            autopct='%1.1f%%',
            startangle=140,
            colors=plt.cm.tab20.colors[:len(yearly_counts)],
            explode=explode,
            shadow=True
        )
        ax4.set_title('Yearly Counts Subscription Distribution', fontsize=14)

       
        plt.suptitle('Subscription Analytics Dashboard', fontsize=18, color='white')

     
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png')

    except Exception as e:
        return f"Error generating analytics graph: {str(e)}"


@couriert3.route('/subscribers', methods=['GET'])
def show_subscribers():
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))  # Redirect to login if no user is in the session

    user = User.query.get(session['user_id'])  # Retrieve the user based on the session

    if not user:  # If the user doesn't exist in the database
        return redirect(url_for('logint1.login'))

    # Fetch subscribers and render the template
    subscribers = Sub.query.all()
    return render_template('subscribers.html', user=user, subscribers=subscribers)



@couriert3.route('/subscribe', methods=['POST'])
def subscribe():
    user = None  

    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))  

   
    user = User.query.get(session['user_id']) if 'user_id' in session else None

    email = request.form.get('email')
    if not email:
        flash("Email is required!", "danger")
        return redirect(url_for('show_subscribers'))
    try:
        new_subscriber = Sub(email=email)
        db.session.add(new_subscriber)
        db.session.commit()
        flash("Subscribed successfully!", "success")
    except Exception as e:
        flash("Email already subscribed or invalid!", "danger")
    return redirect(url_for('show_subscribers',user=user))



@couriert3.route('/api/subscribers', methods=['GET'])
def api_subscribers():
    user = None 

    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))  

   
    user = User.query.get(session['user_id']) if 'user_id' in session else None

    subscribers = Sub.query.order_by(Sub.date_created.desc()).all()
    subscriber_data = [
        {"id": sub.id, "email": sub.email, "date_created": sub.date_created.strftime("%Y-%m-%d %H:%M:%S")}
        for sub in subscribers
    ]
    return {"subscribers": subscriber_data}


@couriert3.route('/delete/<int:sno>', methods=['GET'])
def delete(sno):
    todo = Courier.query.filter_by(sno=sno).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        flash("Order deleted successfully!", "success")
    else:
        flash("Order not found!", "danger")
    return redirect("/")


@couriert3.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    user = None

    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))  

    user = User.query.get(session['user_id']) if 'user_id' in session else None

    # Fetch courier record
    courier = Courier.query.filter_by(sno=sno).first()
    if not courier:
        return "Courier record not found", 404

    if request.method == 'POST':
        try:
            courier.order_id = request.form['orderid']
            courier.courier_name = request.form['courier_name']
            courier.status = request.form['status']

            # Fetch the order
            order = Order.query.get(courier.order_id)
            if order:
                order.status = courier.status  

                # If the order is delivered, set delivery_date and check status
                if courier.status == "Delivered":
                    courier.delivered_at = datetime.utcnow()  # Set actual delivery timestamp
                    order.delivery_date = courier.delivered_at  # Sync with order table

                    # Determine if delivery is On-Time or Late
                    if order.expected_delivery_date:
                        order.delivery_status = "On-Time" if order.delivery_date <= order.expected_delivery_date else "Late"
                    else:
                        order.delivery_status = None  # Fallback case

                # Update order details statuses
                order_details = OrderDetail.query.filter_by(order_id=courier.order_id).all()
                for detail in order_details:
                    detail.status = courier.status

            db.session.commit()  
            flash("Order and related statuses updated successfully!", "success")
        except Exception as e:
            db.session.rollback() 
            flash(f"Error: {e}", "danger")

        return redirect("/courier")  

    return render_template('update.html', todo=courier, user=user)


@couriert3.route('/track', methods=['GET', 'POST'])
def track_order():
    if 'user_id' not in session:
        flash("Please log in to track your order.", "warning")
        return redirect(url_for('logint1.login'))

    user = User.query.get(session['user_id'])
    orders_not_pending = Courier.query.all()
    order = None

    if request.method == 'POST':
       
        manual_order_id = request.form.get('manual_order_id') 
        dropdown_order_id = request.form.get('order_id')       

       
        order_id = manual_order_id if manual_order_id else dropdown_order_id

        if order_id:
            order = Courier.query.filter_by(order_id=order_id).first()
            if order:
                order.status_percentage = {
                    'Dispatched': 20,
                    'In Transit': 40,
                    'Out for Delivery': 60,
                    'Delivered': 80,
                    'Failed Attempt': 100
                }.get(order.status, 0)
            else:
                flash("Order not found!", "danger")
        else:
            flash("Please provide a valid Order ID.", "warning")

    return render_template('track.html', order=order, user=user, orders_not_pending=orders_not_pending)

@couriert3.route('/helpcenter')
def helpcenter():
    user = None  

    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))  

  
    user = User.query.get(session['user_id']) if 'user_id' in session else None

    return render_template('helpcenter.html',user=user)

@couriert3.route('/privacypolicy')
def privacypolicy():
    user = None  

    if 'user_id' not in session:
        return redirect(url_for('logint1.login')) 

    
    user = User.query.get(session['user_id']) if 'user_id' in session else None

    return render_template('privacypolicy.html',user=user)

@couriert3.route('/termsofservice')
def termsofservice():
    user = None  

    if 'user_id' not in session:
        return redirect(url_for('logint1.login')) 

    
    user = User.query.get(session['user_id']) if 'user_id' in session else None

    return render_template('termsofservice.html',user=user)

@couriert3.route("/bellicon")
@couriert3.route("/bellicon.html")
def bell_icon():
    user = None  

    if 'user_id' not in session:
        return redirect(url_for('logint1.login')) 

   
    user = User.query.get(session['user_id']) if 'user_id' in session else None
    return render_template("bellicon.html",user=user)

@couriert3.route("/monitorprogress")
@couriert3.route("/monitor_progress.html")
def monitor_progress():
    user = None  

    if 'user_id' not in session:
        return redirect(url_for('logint1.login')) 

   
    user = User.query.get(session['user_id']) if 'user_id' in session else None

    couriers = Courier.query.all()

  
    total_deliveries = len(couriers)
    delivered_orders_count = len([c for c in couriers if c.status == "Delivered"])
    pending_orders = len([c for c in couriers if c.status not in ["Delivered", "Failed Attempt"]])
    in_transit_orders = len([c for c in couriers if c.status == "In Transit"])

    
    delivered_data = [c.date_created for c in couriers if c.status == "Delivered"]
    delivered_data.sort()
    cumulative_deliveries = list(range(1, len(delivered_data) + 1))

    
    line_fig = Figure()
    line_fig.add_trace(Scatter(
        x=delivered_data,
        y=cumulative_deliveries,
        mode='lines+markers',
        name="Delivered Orders",
        line=dict(color='green')
    ))

    line_fig.update_layout(
        title="Cumulative Delivered Orders Over Time",
        xaxis_title="Timestamp",
        yaxis_title="Cumulative Delivered Orders",
        plot_bgcolor="rgba(0, 255, 0, 0.1)",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
    )

    
    status_count = {status: 0 for status in ['Dispatched', 'Out for Delivery', 'Delivered', 'Failed Attempt', 'In transit']}
    for c in couriers:
        status_count[c.status.capitalize()] += 1


    bar_fig = px.bar(
        x=list(status_count.keys()),
        y=list(status_count.values()),
        labels={'x': 'Delivery Status', 'y': 'Count'},
        title="Delivery Status Distribution",
        color_discrete_sequence=['#4CAF50']  
    )

   
    line_chart_html = pio.to_html(line_fig, full_html=False)
    bar_chart_html = pio.to_html(bar_fig, full_html=False)

    all_orders = Courier.query.all() 
    delivered_orders_list = [order for order in all_orders if order.status == "Delivered"]
    
    return render_template(
        'monitor_progress.html', 
        line_chart_html=line_chart_html, 
        bar_chart_html=bar_chart_html,
        total_deliveries=total_deliveries, 
        delivered_orders_count=delivered_orders_count, 
        pending_orders=pending_orders, 
        in_transit_orders=in_transit_orders,
        all_orders=all_orders,
        user=user,
        delivered_orders_list=delivered_orders_list 
    )

# @couriert3.route("/Report_issue", methods=["GET", "POST"])
# @couriert3.route("/Report_issue.html", methods=["GET", "POST"])
# def report_issue():
#     user = None 

#     if 'user_id' not in session:
#         return redirect(url_for('logint1.login')) 

    
#     user = User.query.get(session['user_id']) if 'user_id' in session else None

#     if request.method == "POST":
#         order_id = request.form.get("order_id")
#         description = request.form.get("description")

#         new_issue = DeliveryIssue(
#             order_id=order_id,
#             description=description,
#             resolve_status="Pending"
#         )
#         db.session.add(new_issue)
#         db.session.commit()
#         flash("Issue reported successfully!", "success")
#         return redirect(url_for('report_issue'))

#     issues = DeliveryIssue.query.all()
#     return render_template("Report_issue.html", issues=issues,user=user)


@couriert3.route("/Report_issue", methods=["GET", "POST"])
@couriert3.route("/Report_issue.html", methods=["GET", "POST"])
def report_issue():
    # Ensure the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('logint1.login'))

    # Get the logged-in user
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if request.method == "POST":
        # Retrieve form data
        order_id = request.form.get("order_id")
        description = request.form.get("description")

        # Create a new issue with the logged-in user's ID
        new_issue = DeliveryIssue(
            user_id=user_id,  # Assign the user ID from the session
            order_id=order_id,
            description=description,
            resolve_status="Pending"
        )

        # Add and commit the issue to the database
        db.session.add(new_issue)
        db.session.commit()

        flash("Issue reported successfully!", "success")
        return redirect(url_for('couriert3.report_issue'))

    # Fetch all issues for display
    issues = DeliveryIssue.query.all()
    return render_template("Report_issue.html", issues=issues, user=user)


@couriert3.route("/remove_issue/<int:issue_id>", methods=["POST"])
def remove_issue(issue_id):
    issue = DeliveryIssue.query.get(issue_id)
    if issue:
        db.session.delete(issue)
        db.session.commit()
        flash("Issue removed successfully.", "success")
    else:
        flash("Issue not found.", "danger")
    return redirect(url_for('couriert3.report_issue'))

