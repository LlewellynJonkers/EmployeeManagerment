from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User,District, Province, CREATED_SEED

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    global CREATED_SEED
    if not CREATED_SEED:
        Province.create_northern_cape()
        District.create_pixley_ka_seme()
        User.create_admin()
        CREATED_SEED = True
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        flash("Invalid username or password")
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        role = request.form.get("role")
        password = generate_password_hash(request.form.get("password"))
        user = User(username=username, password_hash=password,role = role)
        db.session.add(user)
        db.session.commit()
        flash("User created! Please login.")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))