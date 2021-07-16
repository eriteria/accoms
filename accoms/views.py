from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from accoms.extensions import login_manager, db
from accoms.models import Users

site = Blueprint("site", __name__, url_prefix="/")


@site.route("/")
def index():
    return render_template("index.html")


@site.route("/register", methods=["POST"])
def register():
    name = request.form.get('user_name')
    email = request.form.get('user_email')
    course = request.form.get('course')
    password = request.form.get('password')
    matric = request.form.get('matricNumberRegister')
    new_user = Users(name, email, password, course,  matric)
    db.session.add(new_user)
    db.session.commit()
    if login_user(new_user):
        flash("Logged in!")
        return redirect(url_for('site.dashboard'))
    else:
        flash("unable to log you in", 'danger')
    return redirect(url_for('site.user'))


@site.route("/signin", methods=["POST"])
def signin():
    matric = request.form.get('matric_number').upper()
    password = request.form.get('user_password')
    user_login = Users.query.filter_by(matric=matric).first()
    if user_login:
        if check_password_hash(user_login.password, password):
            login_user(user_login)
            flash("Login Successful")
            return redirect(url_for('site.dashboard'))
    else:
        flash('Login Unsuccessful', 'danger')
        return redirect(url_for('site.index'))
    return redirect(url_for('site.index'))


@site.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@login_required
@site.route("/user")
def user():
    return render_template("user.html")

@login_required
@site.route("/commitments")
def commitment():
    return render_template("commitments.html")

@site.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.index'))
