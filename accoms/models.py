from flask import flash, redirect, url_for
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from accoms.extensions import db, login_manager


# student_commitment = db.Table('student_commitment',
#                               db.Column('user_id', db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE')),
#                               db.Column('commitment_id', db.Integer(),
#                                         db.ForeignKey('commitment.id', ondelete='CASCADE')))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(50))
    matric = db.Column(db.String(10), unique=True)
    password = db.Column(db.String(256))
    course = db.Column(db.String(50))
    created_commitments = db.relationship('Commitments', backref='user')
    # commitments

    def __init__(self, name, email, password, course, matric):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password, "sha256")
        self.course = course
        self.matric = matric

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class Commitments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    privacy = db.Column(db.String(3))  # PRI-Private, PUB-Public
    creator_id = db.Column(db.String(10), db.ForeignKey('users.id'))


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)
