from datetime import datetime
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from models import MonitoringAlert, Device
from extensions import db
from monitoring_engine import ping_address
bp=Blueprint("monitoring", __name__)
@bp.get("/alerts")
@login_required
def alerts():
    rows=MonitoringAlert.query.order_by(MonitoringAlert.created_at.desc()).limit(200).all()
    return render_template("alerts.html", alerts=rows)
@bp.get("/api/status")
@login_required
def live_status():
    devices=Device.query.filter(Device.monitoring_enabled.is_(True),Device.ip_address.isnot(None)).all()
    now=datetime.utcnow()
    data=[]
    for d in devices:
        old=d.status
        online,latency=ping_address(d.ip_address)
        new="Online" if online else "Offline"
        d.status=new;d.last_checked=now;d.latency_ms=latency
        if online: d.last_seen=now
        if old not in ("Unknown",new):
            db.session.add(MonitoringAlert(device_id=d.id,device_name=d.name,ip_address=d.ip_address,old_status=old,new_status=new,created_at=now))
        data.append({"id":d.id,"name":d.name,"ip":d.ip_address,"status":new,"latency_ms":latency,"last_checked":now.isoformat(timespec="seconds")+"Z"})
    db.session.commit()
    return jsonify({"devices":data,"checked_at":now.isoformat(timespec="seconds")+"Z"})
monitoring_bp=bp
