from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from models import Alert
from extensions import db

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")

@alerts_bp.get("/")
@login_required
def index():
    alerts=Alert.query.order_by(Alert.created_at.desc()).limit(250).all()
    return render_template("alerts.html", alerts=alerts)

@alerts_bp.post("/<int:alert_id>/acknowledge")
@login_required
def acknowledge(alert_id):
    alert=Alert.query.get_or_404(alert_id)
    if alert.acknowledged_at is None:
        alert.acknowledged_at=datetime.utcnow()
        db.session.commit()
    flash("Alert marked as acknowledged.","success")
    return redirect(url_for("alerts.index"))
