from datetime import datetime
from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required
from models import Customer, Payment
from extensions import db
from routes.admin import admin_required
bp=Blueprint("customers",__name__)

@bp.get("/")
@login_required
def index():
    q=request.args.get("q","").strip()
    status=request.args.get("status","")
    query=Customer.query
    if q:
        query=query.filter(db.or_(Customer.full_name.ilike(f"%{q}%"),Customer.email.ilike(f"%{q}%"),Customer.phone.ilike(f"%{q}%"),Customer.plan.ilike(f"%{q}%")))
    if status in ("Active","Suspended"):
        query=query.filter_by(status=status)
    customers=query.order_by(Customer.id.desc()).all()
    payments=Payment.query.order_by(Payment.paid_at.desc()).limit(100).all()
    return render_template("customers.html",customers=customers,payments=payments,q=q,status_filter=status)

@bp.post("/add")
@login_required
def add():
    name=request.form.get("full_name","").strip()
    try: fee=float(request.form.get("monthly_fee") or 0)
    except ValueError: fee=-1
    if fee<0:
        flash("Amafaranga agomba kuba umubare utari munsi ya zero.","danger"); return redirect(url_for("customers.index"))
    if not name: flash("Andika izina ry'umukiriya.","danger")
    else:
        db.session.add(Customer(full_name=name,email=request.form.get("email","").strip(),phone=request.form.get("phone","").strip(),plan=request.form.get("plan","").strip(),monthly_fee=fee,status=request.form.get("status","Active")))
        db.session.commit(); flash("Umukiriya yongewemo.","success")
    return redirect(url_for("customers.index"))

@bp.post("/<int:item_id>/edit")
@login_required
def edit(item_id):
    c=Customer.query.get_or_404(item_id)
    name=request.form.get("full_name","").strip()
    try: fee=float(request.form.get("monthly_fee") or 0)
    except ValueError: fee=-1
    status=request.form.get("status","Active")
    if not name or fee<0 or status not in ("Active","Suspended"):
        flash("Reba neza amakuru winjije.","danger")
    else:
        c.full_name=name;c.email=request.form.get("email","").strip();c.phone=request.form.get("phone","").strip();c.plan=request.form.get("plan","").strip();c.monthly_fee=fee;c.status=status
        db.session.commit();flash("Amakuru y'umukiriya avuguruwe.","success")
    return redirect(url_for("customers.index"))

@bp.post("/<int:item_id>/payment")
@login_required
def payment(item_id):
    c=Customer.query.get_or_404(item_id)
    try: amount=float(request.form.get("amount",""))
    except ValueError: amount=0
    month=request.form.get("billing_month","")
    try: datetime.strptime(month,"%Y-%m")
    except ValueError: month=""
    if amount<=0 or not month:
        flash("Injiza amafaranga meza n'ukwezi kwishyuwe.","danger")
    else:
        db.session.add(Payment(customer_id=c.id,amount=amount,billing_month=month,notes=request.form.get("notes","").strip()))
        db.session.commit();flash("Payment yanditswe neza.","success")
    return redirect(url_for("customers.index"))

@bp.post("/<int:item_id>/delete")
@admin_required
def delete(item_id):
    c=Customer.query.get_or_404(item_id); db.session.delete(c); db.session.commit()
    flash("Umukiriya n'amateka ye ya payment basibwe.","info"); return redirect(url_for("customers.index"))
customers_bp=bp
