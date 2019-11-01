from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey


class User(UserMixin, db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), index=True, unique=True, nullable=False)
	email = db.Column(db.String(30), index=True, unique=True, nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)
	is_staff = db.Column(db.Boolean, nullable=False)

	bookings = db.relationship('Booking', back_populates='user')

	def __repr__(self):
		return '[ UID:{:0>4} ] {}'.format(self.user_id, self.username)

	def get_id(self):
		return ('User', self.user_id)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


class Admin(UserMixin, db.Model):
	admin_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), index=True, unique=True, nullable=False)
	email = db.Column(db.String(30), index=True, unique=True, nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)

	def __repr__(self):
		return '[ AID:{:0>4} ] {}'.format(self.admin_id, self.username)

	def get_id(self):
		return ('Admin', self.admin_id)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
