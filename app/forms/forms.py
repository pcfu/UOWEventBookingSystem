from app.models.users import User, Admin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,\
					SubmitField, IntegerField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, EqualTo, ValidationError, \
								NumberRange, Email
#from wtforms_components import NumberInput
from datetime import date


class BaseLogin(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

	def authenticate(self, user):
		if user is None:
			error_list = list(self.username.errors)
			error_list.append('Invalid username')
			self.username.errors = tuple(error_list)
			return False
		if not user.check_password(self.password.data):
			error_list = list(self.password.errors)
			error_list.append('Incorrect password')
			self.password.errors = tuple(error_list)
			return False
		return True


class MemberLoginForm(BaseLogin):
	def validate(self):
		user = User.query.filter_by(username=self.username.data).first()
		return super().authenticate(user)


class AdminLoginForm(BaseLogin):
	def validate(self):
		user = User.query.filter_by(username=self.username.data).first()
		return super().authenticate(user) and user.is_staff


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


'''
class BookingForm(FlaskForm):
	title = StringField(render_kw={'readonly':'True'})
	username = StringField(render_kw={'readonly':'True'})
	date = SelectField()
	count = IntegerField('Count', default=1, validators=[DataRequired(), NumberRange(min=1)], widget=NumberInput())
	price = IntegerField('Price', render_kw={'readonly':'True'})
	submit = SubmitField('Book')
'''
