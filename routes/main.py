from flask import Blueprint,render_template
from flask_login import login_required,current_user
from sqlalchemy import func
from models import Device,Customer
from extensions import db
main_bp=Blueprint("main",__name__)
@main_bp.get("/dashboard")
@login_required
def dashboard():
    total=Device.query.count(); online=Device.query.filter_by(status="Online").count()
    offline=Device.query.filter_by(status="Offline").count()
    customers=Customer.query.count()
    revenue=db.session.query(func.coalesce(func.sum(Customer.monthly_fee),0)).scalar()
    return render_template("dashboard.html",user=current_user,total_devices=total,
        online_devices=online,offline_devices=offline,total_customers=customers,
        monthly_revenue=revenue)
