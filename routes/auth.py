from datetime import datetime, timedelta
from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_user,logout_user,login_required,current_user
from extensions import db
from models import User,LoginHistory,LoginAttempt,ActivityLog
auth_bp=Blueprint("auth",__name__)
MAX_ATTEMPTS=5; WINDOW_MINUTES=15

def client_ip():
    return (request.remote_addr or "unknown")[:64]

@auth_bp.route("/",methods=["GET","POST"])
@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email","").strip().lower()[:160]; ip=client_ip(); cutoff=datetime.utcnow()-timedelta(minutes=WINDOW_MINUTES)
        blocked=LoginAttempt.query.filter(LoginAttempt.email==email,LoginAttempt.ip_address==ip,LoginAttempt.created_at>=cutoff).count()>=MAX_ATTEMPTS
        if blocked:
            db.session.add(LoginHistory(email=email,success=False,ip_address=ip));db.session.commit()
            flash("Login temporarily blocked. Tegereza iminota 15 mbere yo kongera kugerageza.","danger")
            return render_template("login.html")
        u=User.query.filter_by(email=email).first()
        if u and u.check_password(request.form.get("password","")):
            LoginAttempt.query.filter_by(email=email,ip_address=ip).delete()
            db.session.add(LoginHistory(email=email,success=True,ip_address=ip));db.session.add(ActivityLog(actor_id=u.id,actor_email=u.email,action="Successful login"));db.session.commit()
            login_user(u,remember=bool(request.form.get("remember")));flash("Winjiye neza muri SmartNet.","success");return redirect(url_for("main.dashboard"))
        db.session.add(LoginAttempt(email=email,ip_address=ip));db.session.add(LoginHistory(email=email,success=False,ip_address=ip));db.session.commit()
        flash("Email cyangwa password si byo.","danger")
    return render_template("login.html")
@auth_bp.post("/logout")
@login_required
def logout():
    db.session.add(ActivityLog(actor_id=current_user.id,actor_email=current_user.email,action="Logout"));db.session.commit()
    logout_user();flash("Wasohotse muri konti yawe.","info");return redirect(url_for("auth.login"))
