from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required
from models import Device
from extensions import db
bp=Blueprint("devices",__name__)
@bp.get("/")
@login_required
def index(): return render_template("devices.html",devices=Device.query.order_by(Device.id.desc()).all())
@bp.post("/add")
@login_required
def add():
    name=request.form.get("name","").strip(); kind=request.form.get("device_type","").strip()
    if not name or not kind: flash("Andika izina n'ubwoko bwa device.","danger")
    else:
        db.session.add(Device(name=name,device_type=kind,ip_address=request.form.get("ip_address","").strip(),
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
@bp.post("/<int:item_id>/delete")
@login_required
def delete(item_id):
    d=Device.query.get_or_404(item_id); db.session.delete(d); db.session.commit()
    flash("Device yasibwe.","info"); return redirect(url_for("devices.index"))
devices_bp=bp
