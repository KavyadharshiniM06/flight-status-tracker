from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    phone      = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    saved_flights = db.relationship("SavedFlight", backref="user", lazy=True)
    search_history = db.relationship("SearchHistory", backref="user", lazy=True)


class SavedFlight(db.Model):
    __tablename__ = "saved_flights"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    iata       = db.Column(db.String(10), nullable=False)
    label      = db.Column(db.String(100), nullable=True)  # e.g. "My Mumbai flight"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SearchHistory(db.Model):
    __tablename__ = "search_history"

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    iata         = db.Column(db.String(10), nullable=False)
    airline      = db.Column(db.String(100), nullable=True)
    status       = db.Column(db.String(50), nullable=True)
    dep_airport  = db.Column(db.String(150), nullable=True)
    arr_airport  = db.Column(db.String(150), nullable=True)
    searched_at  = db.Column(db.DateTime, default=datetime.utcnow)