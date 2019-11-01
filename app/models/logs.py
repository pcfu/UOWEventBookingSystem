from app import db
from sqlalchemy import ForeignKey
from datetime import datetime


class LoginHistory(db.Model):
	in_id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, nullable=False)
	user_id = db.Column(db.Integer, ForeignKey('user.user_id'))
	admin_id = db.Column(db.Integer, ForeignKey('admin.admin_id'))

	#add relationships
	user = db.relationship('User', back_populates='logins')
	admin = db.relationship('Admin', back_populates='logins')


def add_login_record():
	if is_admin_user():
		log = LoginHistory(timestamp=datetime.now(), user_id=current_user.admin_id)
	else:
		log = LoginHistory(timestamp=datetime.now(), admin_id=current_user.user_id)
	db.session.add(log)
	db.session.commit()
