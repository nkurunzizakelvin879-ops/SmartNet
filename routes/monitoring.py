from flask import Blueprint, render_template
from flask_login import login_required
from models import MonitoringAlert
bp=Blueprint("monitoring", __name__)
@bp.get("/alerts")
@login_required
def alerts():
    rows=MonitoringAlert.query.order_by(MonitoringAlert.created_at.desc()).limit(200).all()
    return render_template("alerts.html", alerts=rows)
monitoring_bp=bp
