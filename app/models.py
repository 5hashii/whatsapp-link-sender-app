from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    profile_picture = db.Column(db.String(200), default='default.jpg')
    bio = db.Column(db.String(500))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    links = db.relationship('Link', backref='user', lazy=True)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500))
    description = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sent_numbers = db.relationship('SentNumber', backref='link', lazy=True)

class SentNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20))
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'), nullable=False)
