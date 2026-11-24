from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_user,logout_user,login_required
from models import User
auth_bp=Blueprint("auth",__name__)
@auth_bp.route("/",methods=["GET","POST"])
@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=User.query.filter_by(email=request.form.get("email","").strip().lower()).first()
        if u and u.check_password(request.form.get("password","")):
            login_user(u,remember=bool(request.form.get("remember")))
            flash("Winjiye neza muri SmartNet.","success")
            return redirect(url_for("main.dashboard"))
        flash("Email cyangwa password si byo.","danger")
    return render_template("login.html")
@auth_bp.post("/logout")
@login_required
def logout():
    logout_user(); flash("Wasohotse muri konti yawe.","info")
    return redirect(url_for("auth.login"))
