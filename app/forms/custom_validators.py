from wtforms.validators import ValidationError
from flask_login import current_user
from datetime import datetime


class Interval(object):
	def __init__(self, interval=0.5, message=None):
		self.interval = interval
		if not message:
			message = 'Field must be in intervals of %.2f.' % (interval)
		self.message = message

	def __call__(self, form, field):
		if field.data is None:
			field.data = 0.0
		i = float(field.data)
		if i % self.interval != 0.0:
			raise ValidationError(self.message)


class DateInRange(object):
	def __init__(self, message=None):
		if not message:
			message = 'Date must be after current date.'
		self.message = message

	def __call__(self, form, field):
		if field.data <= datetime.now():
			raise ValidationError(self.message)
