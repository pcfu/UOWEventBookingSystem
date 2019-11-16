from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey


class UserGroup(db.Model):
	__tablename__ = 'usergroup'
	group_id = db.Column(db.Integer, primary_key=True)
	group_name = db.Column(db.String, index=True, unique=True, nullable=False)

	users = db.relationship('User', back_populates='group')


class User(UserMixin, db.Model):
	__tablename__ = 'user'
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), index=True, unique=True, nullable=False)
	email = db.Column(db.String(30), index=True, unique=True, nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)
	group_id = db.Column(db.Integer, ForeignKey('usergroup.group_id'))

	group = db.relationship('UserGroup', back_populates='users')
	#logins = db.relationship('LoginHistory', back_populates='user')
	#logouts = db.relationship('LogoutHistory', back_populates='user')
	#bookings = db.relationship('Booking', back_populates='user')

	def __repr__(self):
		return '[ UID:{:0>4} ] {}'.format(self.user_id, self.username)

	#def get_id(self):
	#	return ('User', self.user_id)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def is_regular(self):
		return self.group.group_name == 'regular'

	def is_staff(self):
		return self.group.group_name == 'staff'

	def is_admin(self):
		return self.group.group_name == 'admin'
