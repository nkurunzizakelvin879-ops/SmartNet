import ipaddress
import platform
import subprocess
import time
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from models import Device, Alert
from extensions import db

bp = Blueprint("devices", __name__)

def ping_device(address):
    """Ping one registered address safely; return latency in ms or None."""
    try: ipaddress.ip_address(address)
    except (ValueError, TypeError): return None
    command = ["ping", "-n", "1", "-w", "1200", address] if platform.system().lower() == "windows" else ["ping", "-c", "1", "-W", "1", address]
    started = time.perf_counter()
    try: result = subprocess.run(command, capture_output=True, text=True, timeout=2.5, check=False)
    except (OSError, subprocess.TimeoutExpired): return None
    return round((time.perf_counter() - started) * 1000, 2) if result.returncode == 0 else None

@bp.get("/")
@login_required
def index():
    return render_template("devices.html", devices=Device.query.order_by(Device.id.desc()).all())

@bp.post("/add")
@login_required
def add():
    name=request.form.get("name","").strip(); kind=request.form.get("device_type","").strip(); ip=request.form.get("ip_address","").strip()
    if ip:
        try: ipaddress.ip_address(ip)
        except ValueError: flash("IP address ntabwo yemewe.","danger"); return redirect(url_for("devices.index"))
    if not name or not kind: flash("Andika izina n'ubwoko bwa device.","danger")
    else:
        db.session.add(Device(name=name,device_type=kind,ip_address=ip,location=request.form.get("location","").strip(),status="Unknown",notes=request.form.get("notes","").strip()))
        db.session.commit(); flash("Device yongewemo.","success")
    return redirect(url_for("devices.index"))

@bp.post("/<int:item_id>/edit")
@login_required
def edit(item_id):
    d=Device.query.get_or_404(item_id)
    name=request.form.get("name","").strip(); kind=request.form.get("device_type","").strip(); ip=request.form.get("ip_address","").strip()
    if ip:
        try: ipaddress.ip_address(ip)
        except ValueError: flash("IP address ntabwo yemewe.","danger"); return redirect(url_for("devices.index"))
    if not name or not kind: flash("Name na Type birakenewe.","danger")
    else:
        d.name=name; d.device_type=kind; d.ip_address=ip or None; d.location=request.form.get("location","").strip(); d.notes=request.form.get("notes","").strip()
        if not ip: d.status="Unknown"; d.latency_ms=None; d.last_seen=None
        db.session.commit(); flash("Device yavuguruwe neza.","success")
    return redirect(url_for("devices.index"))

@bp.post("/monitor")
@login_required
def monitor():
    devices=Device.query.filter(Device.ip_address.isnot(None), Device.ip_address != "").all()
    for device in devices:
        old_status=device.status
        latency=ping_device(device.ip_address)
        new_status="Online" if latency is not None else "Offline"
        device.latency_ms=latency; device.status=new_status
        if latency is not None: device.last_seen=datetime.utcnow()
        if new_status=="Offline" and old_status!="Offline":
            db.session.add(Alert(device_id=device.id,device_name=device.name,title="Device offline",message=f"{device.name} ({device.ip_address}) is unreachable.",severity="warning"))
        elif new_status=="Online" and old_status=="Offline":
            Alert.query.filter_by(device_id=device.id,title="Device offline",resolved_at=None).update({Alert.resolved_at:datetime.utcnow()})
    db.session.commit()
    flash(f"Scan irangiye: {len(devices)} registered IP devices checked.","success")
    return redirect(url_for("devices.index"))

@bp.get("/api/status")
@login_required
def api_status():
    return jsonify([{"id":d.id,"name":d.name,"ip":d.ip_address,"status":d.status,"latency_ms":d.latency_ms,"last_seen":d.last_seen.isoformat() if d.last_seen else None} for d in Device.query.order_by(Device.id.desc()).all()])

@bp.post("/<int:item_id>/status")
@login_required
def status(item_id):
    d=Device.query.get_or_404(item_id); s=request.form.get("status")
    if s in ("Online","Offline","Unknown"): d.status=s; db.session.commit()
    return redirect(url_for("devices.index"))

@bp.post("/<int:item_id>/delete")
@login_required
def delete(item_id):
    d=Device.query.get_or_404(item_id); db.session.delete(d); db.session.commit()
    flash("Device yasibwe.","info"); return redirect(url_for("devices.index"))

devices_bp=bp
