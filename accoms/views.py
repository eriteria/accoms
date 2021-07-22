import json
import os
import uuid

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash
from datetime import datetime

from werkzeug.utils import secure_filename

from accoms.extensions import db
from accoms.models import Users, Commitments
from accoms.settings import UPLOAD_FOLDER

site = Blueprint("site", __name__, url_prefix="/")

# Helper Code
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Routes For Displaying templates
@site.route("/")
def index():
    return render_template("index.html")


@site.route("/dashboard")
@login_required
def dashboard():
    commitments = Commitments.query.filter_by(privacy='public').all()
    # private_commitments = Commitments.query.filter_by(creator=current_user, privacy='private').all()
    # commitments = commitments + private_commitments
    result = []
    for com in commitments:
        if com not in current_user.commitments:
            result.append(com)
    return render_template("dashboard.html", result=result)


@login_required
@site.route("/user")
def user():
    return render_template("user.html")


@login_required
@site.route("/commitments")
def commitment():
    ongoing_commitments = current_user.commitments
    return render_template("commitments.html", ongoing_commitments=ongoing_commitments)


@site.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.index'))


# Routes for doing stuff :)
@site.route("/register", methods=["POST"])
def register():
    name = request.form.get('user_name')
    email = request.form.get('user_email')
    course = request.form.get('course')
    password = request.form.get('password')
    matric = request.form.get('matricNumberRegister').upper()
    user_login = Users.query.filter_by(matric=matric).first()
    if user_login:
        login_user(user_login)
    else:  
        new_user = Users(name, email, password, course, matric)
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


@site.route("/addCommitment", methods=["POST"])
def add_commitment():
    name = request.form.get('commitmentName')
    start = datetime.strptime(request.form.get('startDate'), '%Y-%m-%d')
    end = datetime.strptime(request.form.get('endDate'), '%Y-%m-%d')
    stake = request.form.get('stake')
    privacy = request.form['privacy']
    new_commitment = Commitments(name=name, start_date=start, end_date=end, stake=stake,
                                 privacy=privacy, creator=current_user)
    new_commitment.users.append(current_user)
    db.session.add(new_commitment)
    db.session.commit()
    return redirect(url_for('site.commitment'))

# x = {"NAme": "Joseph"}
@site.route("/joinCommitment", methods=["POST"])
def join_commitment():
    commitment_id = int(json.loads(request.data)['commitmentId'])
    commitment = Commitments.query.get(commitment_id)
    if commitment:
        if current_user.is_authenticated:
            commitment.users.append(current_user)
            db.session.commit()
            return jsonify({"Success": "Successfully joined this commitment"}), 200
    else:
        return jsonify({"error": "Commitment does not exist"}), 404
    return jsonify({})


@site.route("/dishonourCommitment", methods=["POST"])
def dishonor_commitment():
    commitment_id = int(json.loads(request.data)['commitmentId'])
    commitment = Commitments.query.get(commitment_id)
    if commitment:
        if current_user.is_authenticated:
            if current_user in commitment.users:
                commitment.users.remove(current_user)
                current_user.dishonoured_commitments.append(commitment)
                db.session.commit()
                return jsonify({"Success": "Successfully dishonoured this commitment"}), 200
            else:
                return jsonify({"error": "You are not part of this commitment"}), 401
    else:
        return jsonify({"error": "Commitment does not exist"}), 404
    return jsonify({})


@site.route("/honourCommitment/<commitment_id>", methods=["POST"])
def honour_commitment(commitment_id):
    """

    :param commitment_id:
    """
    # file = request.files['proof']
    # if file.filename == '':
    #     flash("Please upload a valid file", "Error")
    #     return redirect(url_for("site.commitment"))
    # if file and allowed_file(file.filename):
    #     if os.path.exists(UPLOAD_FOLDER + "/" + file.filename):  # if image with same name exists
    #         _dot = file.filename.find(".")
    #         file.filename = file.filename[:_dot] + str(uuid.uuid4()) + file.filename[_dot:]
    #     filename = secure_filename(file.filename)
    #     file.save(os.path.normpath(os.path.join(UPLOAD_FOLDER, filename)))
    commitment = Commitments.query.get(commitment_id)
    if commitment:
        if current_user.is_authenticated:
            if current_user in commitment.users:
                commitment.users.remove(current_user)
                current_user.honoured_commitments.append(commitment)
                db.session.commit()
                flash("Success", "success")
                return redirect(url_for('site.commitment'))
            else:
                flash("You are not part of this commitment", "error")
                return redirect(url_for('site.commitment'))
        else:
            flash("You are not allowed", "warning")
        return redirect(url_for('site.commitment'))
    return redirect(url_for('site.commitment'))
