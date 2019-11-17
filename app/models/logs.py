from app import db
from sqlalchemy import ForeignKey
#from sqlalchemy.ext.hybrid import hybrid_property
from app.models.users import User
#from flask_login import current_user
#from datetime import datetime


class LoginHistory(db.Model):
	__tablename__ = 'login_history'
	in_id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, nullable=False)
	user_id = db.Column(db.Integer, ForeignKey('user.user_id'))

	#add relationships
	user = db.relationship('User', back_populates='logins')

	'''
	@hybrid_property
	def is_regular(self):
		if self.user:
			return not self.user.is_staff()
		else:
			return False

	@is_regular.expression
	def is_regular(cls):
		return db.exists().where(db.and_(User.user_id == cls.user_id,
										 User.is_staff == False))\
						  .correlate(cls)

	@hybrid_property
	def is_staff(self):
		if self.user:
			return self.user.is_staff()
		else:
			return False

	@is_staff.expression
	def is_staff(cls):
		return db.exists().where(db.and_(User.user_id == cls.user_id,
										 User.is_staff == True))\
						  .correlate(cls)

	@hybrid_property
	def is_admin(self):
		return self.admin

	@is_admin.expression
	def is_admin(cls):
		return db.exists().where(db.and_(Admin.admin_id == cls.admin_id))\
						  .correlate(cls)
	'''


class LogoutHistory(db.Model):
	__tablename__ = 'logout_history'
	out_id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime, nullable=False)
	user_id = db.Column(db.Integer, ForeignKey('user.user_id'))

	#add relationships
	user = db.relationship('User', back_populates='logouts')

	'''
	@hybrid_property
	def is_regular(self):
		if self.user:
			return not self.user.is_staff()
		else:
			return False

	@is_regular.expression
	def is_regular(cls):
		return db.exists().where(db.and_(User.user_id == cls.user_id,
										 User.is_staff == False))\
						  .correlate(cls)

	@hybrid_property
	def is_staff(self):
		if self.user:
			return self.user.is_staff()
		else:
			return False

	@is_staff.expression
	def is_staff(cls):
		return db.exists().where(db.and_(User.user_id == cls.user_id,
										 User.is_staff == True))\
						  .correlate(cls)

	@hybrid_property
	def is_admin(self):
		return self.admin

	@is_admin.expression
	def is_admin(cls):
		return db.exists().where(db.and_(Admin.admin_id == cls.admin_id))\
						  .correlate(cls)
	'''
