import csv
import io
from datetime import datetime
from flask import Blueprint,render_template,request,redirect,url_for,flash,make_response
from flask_login import login_required, current_user
from models import Customer, Payment, ActivityLog
from extensions import db
from routes.admin import admin_required
bp=Blueprint("customers",__name__)

def filtered_customers(q="", status=""):
    query=Customer.query
    if q:
        query=query.filter(db.or_(Customer.full_name.ilike(f"%{q}%"),Customer.email.ilike(f"%{q}%"),Customer.phone.ilike(f"%{q}%"),Customer.plan.ilike(f"%{q}%")))
    if status in ("Active","Suspended"):
        query=query.filter_by(status=status)
    return query.order_by(Customer.id.desc())

def csv_response(filename, rows):
    stream=io.StringIO()
    writer=csv.writer(stream)
    writer.writerows(rows)
    response=make_response("\ufeff"+stream.getvalue())
    response.headers["Content-Type"]="text/csv; charset=utf-8"
    response.headers["Content-Disposition"]=f'attachment; filename="{filename}"'
    return response

@bp.get("/")
@login_required
def index():
    q=request.args.get("q","").strip()
    status=request.args.get("status","")
    billing_month=request.args.get("billing_month",datetime.utcnow().strftime("%Y-%m"))
    try: datetime.strptime(billing_month,"%Y-%m")
    except ValueError: billing_month=datetime.utcnow().strftime("%Y-%m")
    customers=filtered_customers(q,status).all()
    payments=Payment.query.order_by(Payment.paid_at.desc()).limit(100).all()
    monthly_payments=Payment.query.filter_by(billing_month=billing_month).all()
    paid_by_customer={}
    for p in monthly_payments: paid_by_customer[p.customer_id]=paid_by_customer.get(p.customer_id,0)+p.amount
    billing_rows=[{"customer":customer,"paid":paid_by_customer.get(customer.id,0),"fee":customer.monthly_fee or 0,"balance":max(0,(customer.monthly_fee or 0)-paid_by_customer.get(customer.id,0))} for customer in customers]
    billing_total=sum(row["fee"] for row in billing_rows)
    billing_paid=sum(row["paid"] for row in billing_rows)
    billing_balance=sum(row["balance"] for row in billing_rows)
    return render_template("customers.html",customers=customers,payments=payments,q=q,status_filter=status,billing_month=billing_month,billing_rows=billing_rows,billing_total=billing_total,billing_paid=billing_paid,billing_balance=billing_balance)

@bp.get("/export")
@login_required
def export_customers():
    q=request.args.get("q","").strip()
    status=request.args.get("status","")
    customers=filtered_customers(q,status).all()
    rows=[["Customer ID","Full name","Email","Phone","Plan","Monthly fee (RWF)","Status","Created"]]
    rows.extend([[c.id,c.full_name,c.email or "",c.phone or "",c.plan or "",c.monthly_fee or 0,c.status,c.created_at.strftime("%Y-%m-%d") if c.created_at else ""] for c in customers])
    return csv_response("smartnet_customers.csv",rows)

@bp.get("/export-billing")
@login_required
def export_billing():
    q=request.args.get("q","").strip()
    status=request.args.get("status","")
    month=request.args.get("billing_month",datetime.utcnow().strftime("%Y-%m"))
    try: datetime.strptime(month,"%Y-%m")
    except ValueError: month=datetime.utcnow().strftime("%Y-%m")
    customers=filtered_customers(q,status).all()
    payments=Payment.query.filter_by(billing_month=month).all()
    paid_by_customer={}
    for p in payments: paid_by_customer[p.customer_id]=paid_by_customer.get(p.customer_id,0)+p.amount
    rows=[["Billing month",month],[],["Customer ID","Customer","Status","Monthly fee (RWF)","Paid (RWF)","Balance (RWF)"]]
    for c in customers:
        fee=c.monthly_fee or 0
        paid=paid_by_customer.get(c.id,0)
        rows.append([c.id,c.full_name,c.status,fee,paid,max(0,fee-paid)])
    return csv_response(f"smartnet_billing_{month}.csv",rows)

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

@bp.get("/payment/<int:payment_id>/receipt")
@login_required
def receipt(payment_id):
    payment_record=Payment.query.get_or_404(payment_id)
    return render_template("payment_receipt.html",payment=payment_record)

@bp.post("/<int:item_id>/delete")
@admin_required
def delete(item_id):
    c=Customer.query.get_or_404(item_id)
    db.session.add(ActivityLog(actor_id=current_user.id,actor_email=current_user.email,action="Deleted customer "+c.full_name+" (customer ID "+str(c.id)+") and payment history"))
    db.session.delete(c); db.session.commit()
    flash("Umukiriya n'amateka ye ya payment basibwe.","info"); return redirect(url_for("customers.index"))
customers_bp=bp