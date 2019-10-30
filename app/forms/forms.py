from flask_wtf import FlaskForm
from app import db
from app.models.users import User, Admin
from app.models.events import Event, EventSlot
from wtforms import StringField, PasswordField, BooleanField, \
					SubmitField, IntegerField, SelectField, DecimalField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, EqualTo, ValidationError, \
								NumberRange, Email
from wtforms_components import NumberInput
from sqlalchemy.sql import func
from app.query import staff_user_query
from datetime import date


def RaiseError(field, message='Invalid data'):
	error_list = list(field.errors)
	error_list.append(message)
	field.errors = tuple(error_list)


class BaseLogin(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

	### TRY MOVING CHILD authentication into Base again
	def authenticate(self, user):
		if user is None:
			RaiseError(self.username, message='Invalid username')
			return False
		if not user.check_password(self.password.data):
			RaiseError(self.password, message='Incorrect password')
			return False
		return True


class MemberLoginForm(BaseLogin):
	def validate(self):
		user = User.query.filter(User.is_staff == False,
								 User.username == self.username.data).first()
		return super().authenticate(user)


class StaffLoginForm(BaseLogin):
	def validate(self):
		target_name = self.username.data
		staff = staff_user_query(target_name)
		return super().authenticate(staff)


class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',
		validators=[DataRequired(),
					EqualTo('password', message='Password must match!')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Username already taken')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Email already taken')


class SearchForm(FlaskForm):
	CHOICES = [('title', 'Title'),
			   ('date', 'Date'),
			   ('type', 'Type' ),
			   ('price', 'Price')]
	RANGES = [('free', 'FREE'),
			  ('cheap', '< $20'),
			  ('mid', '$20 - 50'),
			  ('expensive', '> $50')]
	STRING_FIELD = StringField()
	DATE_FIELD = DateField(default=date.today())
	PRICE_FIELD = SelectField(choices=RANGES)

	search_field = STRING_FIELD
	search_type = SelectField(choices=CHOICES)
	submit_search = SubmitField('Search')


class BookingForm(FlaskForm):
	title = StringField(render_kw={'readonly':'True'})
	username = StringField(render_kw={'readonly':'True'})
	dates = SelectField(choices=[])
	times = SelectField(choices=[])
	count = IntegerField('Count', default=1,
						 validators=[DataRequired(), NumberRange(min=1)],
						 widget=NumberInput())
	price = DecimalField('Price', render_kw={'readonly':'True'}, places=2)
	submit = SubmitField('Book')

	def preload(self, user, eid):
		event = Event.query.get(eid)
		self.title.data = event.title
		self.username.data = user.username

		# Get dates
		date_records = \
			db.session.query(func.DATE(EventSlot.event_date).label('date'))\
					  .filter(EventSlot.event_id == eid)\
					  .order_by(EventSlot.event_date).all()
		date_list = []
		for rec in date_records:
			if rec.date not in date_list:
				date_list.append(rec.date)
				self.dates.choices.append((rec.date, rec.date))
		self.dates.data = date_list[0]	#set first item as pre-selected default

		# Get timings for pre-selected date
		timings = db.session.query(EventSlot.slot_id,
								func.TIME(EventSlot.event_date).label('time'))\
							.filter(EventSlot.event_id == event.event_id,
								func.DATE(EventSlot.event_date) == self.dates.data)\
							.order_by(EventSlot.event_date).all()
		self.times.choices = [(timing.slot_id, timing.time) for timing in timings]

		self.price.data = event.price
		self.capacity = event.capacity
