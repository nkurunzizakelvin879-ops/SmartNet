from functools import wraps
from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from extensions import db
from models import User,ActivityLog
admin_bp=Blueprint("admin",__name__,url_prefix="/admin")
def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapped(*args,**kwargs):
        if current_user.role!="admin":
            flash("Ntufite uburenzira bwo gukora icyo gikorwa.","danger")
            return redirect(url_for("main.dashboard"))
        return fn(*args,**kwargs)
    return wrapped
def record(actor,action):
    db.session.add(ActivityLog(actor_id=actor.id,actor_email=actor.email,action=action))
@admin_bp.get("/")
@admin_required
def index():
    users=User.query.order_by(User.id.asc()).all()
    logs=ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(150).all()
    return render_template("admin_users.html",users=users,logs=logs)
@admin_bp.post("/create")
@admin_required
def create():
    name=request.form.get("full_name","").strip()
    email=request.form.get("email","").strip().lower()
    password=request.form.get("password","")
    role=request.form.get("role","staff")
    if not name or not email or len(password)<8 or role not in ("admin","staff"):
        flash("Reba neza amakuru; password igomba nibura inyuguti 8.","danger")
    elif User.query.filter_by(email=email).first():
        flash("Email isanzwe ikoreshwa.","danger")
    else:
        user=User(full_name=name,email=email,role=role);user.set_password(password)
        db.session.add(user);db.session.flush()
        record(current_user,"Created account "+email+" ("+role+")")
        db.session.commit();flash("Konti nshya yakozwe.","success")
    return redirect(url_for("admin.index"))
@admin_bp.post("/<int:user_id>/delete")
@admin_required
def delete(user_id):
    target=User.query.get_or_404(user_id)
    if target.id==current_user.id:
        flash("Ntushobora gusiba konti uri gukoresha.","danger")
    elif target.role=="admin" and User.query.filter_by(role="admin").count()<=1:
        flash("Admin wa nyuma ntashobora gusibwa.","danger")
    else:
        email=target.email
        db.session.delete(target);db.session.flush()
        record(current_user,"Deleted account "+email)
        db.session.commit();flash("Konti yasibwe.","success")
    return redirect(url_for("admin.index"))
