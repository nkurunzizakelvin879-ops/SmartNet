from datetime import datetime, timedelta
from flask import Blueprint,render_template
from flask_login import login_required
from models import LoginHistory,LoginAttempt
from routes.admin import admin_required
security_bp=Blueprint("security",__name__,url_prefix="/admin/security")
@security_bp.get("/")
@admin_required
def index():
    history=LoginHistory.query.order_by(LoginHistory.created_at.desc()).limit(300).all()
    cutoff=datetime.utcnow()-timedelta(minutes=15)
    attempts=LoginAttempt.query.filter(LoginAttempt.created_at>=cutoff).order_by(LoginAttempt.created_at.desc()).limit(200).all()
    return render_template("security.html",history=history,attempts=attempts)
