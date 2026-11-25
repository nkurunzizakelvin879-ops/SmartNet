from datetime import datetime
import ipaddress
from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required
from models import Device, MonitoringAlert
from extensions import db
from monitoring_engine import ping_address
bp=Blueprint("devices",__name__)
def _valid_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False
@bp.get("/")
@login_required
def index(): return render_template("devices.html",devices=Device.query.order_by(Device.id.desc()).all())
@bp.post("/add")
@login_required
def add():
    name=request.form.get("name","").strip(); kind=request.form.get("device_type","").strip()
    ip=request.form.get("ip_address","").strip()
    if not name or not kind: flash("Andika izina n'ubwoko bwa device.","danger")
    elif ip and not _valid_ip(ip): flash("IP address wanditse ntabwo ari valid.","danger")
    elif ip and Device.query.filter(Device.ip_address == ip).first(): flash("Iyi IP address isanzwe ikoreshwa n'indi device. Reba IP conflict.","warning")
    else:
        db.session.add(Device(name=name,device_type=kind,ip_address=ip or None,
          location=request.form.get("location","").strip(),status=request.form.get("status","Unknown"),
          notes=request.form.get("notes","").strip()))
        db.session.commit(); flash("Device yongewemo.","success")
    return redirect(url_for("devices.index"))
@bp.post("/<int:item_id>/status")
@login_required
def status(item_id):
    d=Device.query.get_or_404(item_id); s=request.form.get("status")
    if s in ("Online","Offline","Unknown"): d.status=s; db.session.commit()
    return redirect(url_for("devices.index"))
@bp.post("/<int:item_id>/check")
@login_required
def check(item_id):
    d=Device.query.get_or_404(item_id)
    if not d.ip_address:
        flash("Iyi device nta IP address ifite. Yongeremo IP mbere yo kuyipima.","warning")
        return redirect(url_for("devices.index"))
    old=d.status
    online,latency=ping_address(d.ip_address)
    new="Online" if online else "Offline"
    now=datetime.utcnow()
    d.status=new; d.last_checked=now; d.latency_ms=latency
    if online: d.last_seen=now
    if old != new and old != "Unknown":
        db.session.add(MonitoringAlert(device_id=d.id,device_name=d.name,ip_address=d.ip_address,
            old_status=old,new_status=new,created_at=now))
    db.session.commit()
    flash(f"{d.name}: {new}"+(f" ({latency} ms)" if latency is not None else ""),"success" if online else "warning")
    return redirect(url_for("devices.index"))
@bp.post("/<int:item_id>/delete")
@login_required
def delete(item_id):
    d=Device.query.get_or_404(item_id)
    MonitoringAlert.query.filter_by(device_id=d.id).delete()
    db.session.delete(d); db.session.commit()
    flash("Device yasibwe.","info"); return redirect(url_for("devices.index"))
devices_bp=bp
