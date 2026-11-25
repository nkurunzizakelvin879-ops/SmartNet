from datetime import datetime
from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required
from sqlalchemy import func
from extensions import db
from models import Customer,Payment
bp=Blueprint("payments",__name__)
@bp.get("/")
@login_required
def index():
 month=request.args.get("month") or datetime.utcnow().strftime("%Y-%m");customers=Customer.query.filter_by(status="Active").order_by(Customer.full_name.asc()).all();totals=db.session.query(Payment.customer_id,func.sum(Payment.amount)).filter(Payment.billing_month==month).group_by(Payment.customer_id).all();paid_by_customer={cid:amount or 0 for cid,amount in totals};rows=Payment.query.filter_by(billing_month=month).order_by(Payment.paid_at.desc()).all();paid_total=sum(p.amount for p in rows);due_total=sum(max((c.monthly_fee or 0)-paid_by_customer.get(c.id,0),0) for c in customers)
 return render_template("payments.html",customers=customers,rows=rows,month=month,paid_by_customer=paid_by_customer,paid_total=paid_total,due_total=due_total)
@bp.post("/add")
@login_required
def add():
 customer_id=request.form.get("customer_id",type=int);month=request.form.get("billing_month","").strip();method=request.form.get("payment_method","Cash").strip();reference=request.form.get("reference","").strip()
 try:amount=float(request.form.get("amount",""))
 except (TypeError,ValueError):amount=0
 customer=Customer.query.get(customer_id) if customer_id else None
 if not customer or not month or len(month)!=7 or amount<=0:flash("Customer, billing month, and positive amount are required.","danger");return redirect(url_for("payments.index",month=month or datetime.utcnow().strftime("%Y-%m")))
 db.session.add(Payment(customer_id=customer.id,amount=amount,billing_month=month,payment_method=method,reference=reference));db.session.commit();flash("Payment recorded successfully.","success");return redirect(url_for("payments.index",month=month))
@bp.post("/<int:payment_id>/delete")
@login_required
def delete(payment_id):
 p=Payment.query.get_or_404(payment_id);month=p.billing_month;db.session.delete(p);db.session.commit();flash("Payment record removed.","info");return redirect(url_for("payments.index",month=month))
payments_bp=bp
