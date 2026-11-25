from flask import Blueprint,render_template
from flask_login import login_required,current_user
from sqlalchemy import func
from datetime import datetime
from models import Device,Customer,Payment
from extensions import db
main_bp=Blueprint("main",__name__)
@main_bp.get("/dashboard")
@login_required
def dashboard():
 total=Device.query.count();online=Device.query.filter_by(status="Online").count();offline=Device.query.filter_by(status="Offline").count();unknown=total-online-offline;customers=Customer.query.count();active=Customer.query.filter_by(status="Active").count();inactive=customers-active;month=datetime.utcnow().strftime("%Y-%m");revenue=db.session.query(func.coalesce(func.sum(Payment.amount),0)).filter(Payment.billing_month==month).scalar();recent_devices=Device.query.order_by(Device.created_at.desc()).limit(5).all();recent_customers=Customer.query.order_by(Customer.created_at.desc()).limit(5).all();recent_payments=Payment.query.order_by(Payment.paid_at.desc()).limit(5).all()
 return render_template("dashboard.html",user=current_user,total_devices=total,online_devices=online,offline_devices=offline,unknown_devices=unknown,total_customers=customers,active_customers=active,inactive_customers=inactive,monthly_revenue=revenue,recent_devices=recent_devices,recent_customers=recent_customers,recent_payments=recent_payments,now_month=month)
