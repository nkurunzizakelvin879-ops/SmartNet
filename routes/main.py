from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from models import Device, Customer
from extensions import db
main_bp = Blueprint("main", __name__)
def overview_stats():
    total=Device.query.count(); online=Device.query.filter_by(status="Online").count(); offline=Device.query.filter_by(status="Offline").count(); unknown=max(0,total-online-offline)
    customers=Customer.query.count(); active=Customer.query.filter_by(status="Active").count(); inactive=customers-active
    revenue=db.session.query(func.coalesce(func.sum(Customer.monthly_fee),0)).filter(Customer.status=="Active").scalar()
    return dict(total_devices=total,online_devices=online,offline_devices=offline,unknown_devices=unknown,total_customers=customers,active_customers=active,inactive_customers=inactive,monthly_revenue=float(revenue or 0))
@main_bp.get("/dashboard")
@login_required
def dashboard():
    stats=overview_stats(); recent_devices=Device.query.order_by(Device.created_at.desc()).limit(5).all(); recent_customers=Customer.query.order_by(Customer.created_at.desc()).limit(5).all()
    return render_template("dashboard.html",user=current_user,**stats,recent_devices=recent_devices,recent_customers=recent_customers)
@main_bp.get("/dashboard/api/overview")
@login_required
def dashboard_overview_api():
    return jsonify(overview_stats())
