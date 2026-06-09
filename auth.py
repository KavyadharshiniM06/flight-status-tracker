from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from models import db, User

auth   = Blueprint("auth", __name__)
def get_bcrypt():
    # Import here to avoid circular imports
    from web import bcrypt
    return bcrypt



@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        phone    = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("auth.register"))

        bcrypt = get_bcrypt()
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        user   = User(name=name, email=email, phone=phone, password=hashed)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created successfully!", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user     = User.query.filter_by(email=email).first()
        
        bcrypt = get_bcrypt()
        if not user or not bcrypt.check_password_hash(user.password, password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("index"))

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
