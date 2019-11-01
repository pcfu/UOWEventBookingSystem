from app import db
from sqlalchemy import ForeignKey


class LoginHistory(db.Model):
	in_id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, nullable=False)
	user_id = db.Column(db.Integer, ForeignKey('user.user_id'))
	admin_id = db.Column(db.Integer, ForeignKey('admin.admin_id'))

	#add relationships
	user = db.relationship('User', back_populates='logins')
