from app import db
from sqlalchemy import ForeignKey
from app.models.users import User


class LoginHistory(db.Model):
	__tablename__ = 'login_history'
	in_id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, nullable=False)
	user_id = db.Column(db.Integer, ForeignKey('user.user_id'))

	#add relationships
	user = db.relationship('User', back_populates='logins')


class LogoutHistory(db.Model):
	__tablename__ = 'logout_history'
	out_id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, nullable=False)
	user_id = db.Column(db.Integer, ForeignKey('user.user_id'))

	#add relationships
	user = db.relationship('User', back_populates='logouts')
