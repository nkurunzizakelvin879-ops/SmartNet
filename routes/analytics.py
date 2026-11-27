from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from sqlalchemy import func
from models import Device, PingSample

analytics_bp=Blueprint("analytics",__name__,url_prefix="/analytics")

def report():
    cutoff=datetime.utcnow()-timedelta(hours=24)
    devices=Device.query.order_by(Device.name.asc()).all()
    rows=[]
    for d in devices:
        samples=PingSample.query.filter(PingSample.device_id==d.id,PingSample.sampled_at>=cutoff).order_by(PingSample.sampled_at.asc()).all()
        total=len(samples); online=sum(1 for s in samples if s.status=="Online")
        lat=[s.latency_ms for s in samples if s.latency_ms is not None]
        rows.append({"id":d.id,"name":d.name,"ip":d.ip_address or "-","samples":total,"online":online,"availability":round(online*100/total,1) if total else None,"avg_latency":round(sum(lat)/len(lat),2) if lat else None})
    samples=PingSample.query.filter(PingSample.sampled_at>=cutoff).order_by(PingSample.sampled_at.asc()).all()
    trend={"labels":[s.sampled_at.strftime("%H:%M") for s in samples[-180:]],"latency":[s.latency_ms for s in samples[-180:]],"status":[1 if s.status=="Online" else 0 for s in samples[-180:]]}
    total=len(samples); online=sum(1 for s in samples if s.status=="Online"); latency=[s.latency_ms for s in samples if s.latency_ms is not None]
    overall={"total":total,"availability":round(online*100/total,1) if total else None,"avg_latency":round(sum(latency)/len(latency),2) if latency else None,"devices":len(devices)}
    return rows,trend,overall

@analytics_bp.get("/")
@login_required
def index():
    rows,trend,overall=report()
    return render_template("analytics.html",rows=rows,trend=trend,overall=overall)

@analytics_bp.get("/api")
@login_required
def api():
    rows,trend,overall=report()
    return jsonify({"devices":rows,"trend":trend,"overall":overall})
