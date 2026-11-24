from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required
from models import Customer
from extensions import db
bp=Blueprint("customers",__name__)
@bp.get("/")
@login_required
def index(): return render_template("customers.html",customers=Customer.query.order_by(Customer.id.desc()).all())
@bp.post("/add")
@login_required
def add():
    name=request.form.get("full_name","").strip()
    try: fee=float(request.form.get("monthly_fee") or 0); assert fee>=0
    except (ValueError,AssertionError):
        flash("Amafaranga agomba kuba umubare utari munsi ya zero.","danger"); return redirect(url_for("customers.index"))
    if not name: flash("Andika izina ry'umukiriya.","danger")
    else:
        db.session.add(Customer(full_name=name,email=request.form.get("email","").strip(),
          phone=request.form.get("phone","").strip(),plan=request.form.get("plan","").strip(),
          monthly_fee=fee,status=request.form.get("status","Active")))
        db.session.commit(); flash("Umukiriya yongewemo.","success")
    return redirect(url_for("customers.index"))
@bp.post("/<int:item_id>/delete")
@login_required
def delete(item_id):
    c=Customer.query.get_or_404(item_id); db.session.delete(c); db.session.commit()
    flash("Umukiriya yasibwe.","info"); return redirect(url_for("customers.index"))
customers_bp=bp
