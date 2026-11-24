import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import User

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        action = request.form.get("action", "profile")

        if action == "profile":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            if not full_name or not email:
                flash("Andika amazina na email byombi.", "danger")
            elif not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
                flash("Email wanditse ntabwo ari yo.", "danger")
            elif User.query.filter(User.email == email, User.id != current_user.id).first():
                flash("Iyo email isanzwe ikoreshwa n'indi konti.", "danger")
            else:
                current_user.full_name = full_name
                current_user.email = email
                db.session.commit()
                flash("Username na profile byahinduwe neza.", "success")
                return redirect(url_for("settings.index"))

        elif action == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            if not current_user.check_password(current_password):
                flash("Password ukoresha ubu si yo.", "danger")
            elif len(new_password) < 8:
                flash("Password nshya igomba kugira nibura inyuguti 8.", "danger")
            elif new_password != confirm_password:
                flash("Password nshya n'iyo wasubiyemo ntibihura.", "danger")
            elif current_user.check_password(new_password):
                flash("Hitamo password itandukanye n'iyo ukoresha ubu.", "danger")
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash("Password yahinduwe neza. Ongera winjire ukoresheje password nshya.", "success")
                from flask_login import logout_user
                logout_user()
                return redirect(url_for("auth.login"))
        else:
            flash("Icyo wasabye nticyumvikanye.", "danger")

    return render_template("settings.html")
