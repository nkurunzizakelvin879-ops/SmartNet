from datetime import datetime
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from sqlalchemy import or_
from models import MonitoringAlert, Device
from extensions import db
from monitoring_engine import ping_address

bp = Blueprint("monitoring", __name__)


@bp.get("/alerts")
@login_required
def alerts():
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    page = max(request.args.get("page", 1, type=int) or 1, 1)

    query = MonitoringAlert.query
    if search:
        term = f"%{search}%"
        query = query.filter(or_(MonitoringAlert.device_name.ilike(term),
                                 MonitoringAlert.ip_address.ilike(term)))
    if status in ("Online", "Offline"):
        query = query.filter(MonitoringAlert.new_status == status)

    pagination = query.order_by(MonitoringAlert.created_at.desc()).paginate(
        page=page, per_page=25, error_out=False
    )
    return render_template("alerts.html", alerts=pagination.items,
                           pagination=pagination, search=search, status=status)


@bp.get("/api/status")
@login_required
def live_status():
    devices = Device.query.filter(
        Device.monitoring_enabled.is_(True), Device.ip_address.isnot(None)
    ).all()
    now = datetime.utcnow()
    data = []
    for d in devices:
        old = d.status
        online, latency = ping_address(d.ip_address)
        new = "Online" if online else "Offline"
        d.status = new
        d.last_checked = now
        d.latency_ms = latency
        if online:
            d.last_seen = now
        if old not in ("Unknown", new):
            db.session.add(MonitoringAlert(
                device_id=d.id, device_name=d.name, ip_address=d.ip_address,
                old_status=old, new_status=new, created_at=now
            ))
        data.append({"id": d.id, "name": d.name, "ip": d.ip_address,
                     "status": new, "latency_ms": latency,
                     "last_checked": now.isoformat(timespec="seconds") + "Z"})
    db.session.commit()
    return jsonify({"devices": data, "checked_at": now.isoformat(timespec="seconds") + "Z"})


monitoring_bp = bp
