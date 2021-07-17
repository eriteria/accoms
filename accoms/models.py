from flask import flash, redirect, url_for
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from accoms.extensions import db, login_manager

# users_commitments = db.Table('users_commitments', db.Column('user_id', db.ForeignKey('users.id')),
#                              db.Column('commitment_id'), db.ForeignKey('commitment.id'))

users_commitments = db.Table('users_commitments',
                             db.Column('users_commitments', db.Integer, db.ForeignKey('users.id')),
                             db.Column('commitments_id', db.Integer, db.ForeignKey('commitments.id'))
                             )
honoured_commitments = db.Table('honoured_commitments',
                                db.Column('users_commitments', db.Integer, db.ForeignKey('users.id')),
                                db.Column('commitments_id', db.Integer, db.ForeignKey('commitments.id'))
                                )
dishonoured_commitments = db.Table('dishonoured_commitments',
                                   db.Column('users_commitments', db.Integer, db.ForeignKey('users.id')),
                                   db.Column('commitments_id', db.Integer, db.ForeignKey('commitments.id'))
                                   )


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(50))
    matric = db.Column(db.String(10), unique=True)
    password = db.Column(db.String(256))
    course = db.Column(db.String(50))
    # created_commitments = db.relationship('Commitments', backref='user', lazy='dynamic')
    commitments = db.relationship('Commitments', secondary=users_commitments,
                                  backref=db.backref('users', lazy='dynamic'))
    honoured_commitments = db.relationship('Commitments', secondary=honoured_commitments,
                                           backref=db.backref('honoured_users', lazy='dynamic'))
    dishonoured_commitments = db.relationship('Commitments', secondary=dishonoured_commitments,
                                              backref=db.backref('dishonoured_users', lazy='dynamic'))

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
    stake = db.Column(db.Integer)
    privacy = db.Column(db.String(7))
    creator_id = db.Column('creator_id', db.Integer, db.ForeignKey('users.id'))
    creator = db.relationship('Users',
                              backref=db.backref('created_commitment', lazy=True))
    # users = db.relationship('users', backref=db.backref('commitments', lazy=True))


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)
