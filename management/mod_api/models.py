import datetime
from management import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(120))
    pictures = db.relationship("Picture", back_populates="user")

    def __init__(self, firstname, lastname, email=None):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email


class Picture(db.Model):
    __tablename__ = 'picture'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="pictures")

    def __init__(self, path, user):
        self.path = path
        self.user = user


class LogRecognize(db.Model):
    __tablename__ = 'log_recognize'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Boolean)
    date = db.Column(db.DateTime)

    def __init__(self, value):
        self.value = value
        self.date = datetime.datetime.now()
