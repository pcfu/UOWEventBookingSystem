from datetime import date
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
					IntegerField, SelectField, FloatField
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Optional
from app.models import User, Staff


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
		user = Staff.query.filter_by(username=self.username.data).first()
		return super().authenticate(user)


class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',
		validators=[DataRequired(),
					EqualTo('password', message='Password must match!')
					])
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
	KEYWORD = StringField()
	DATE = DateField(default=date.today())
	PRICE = SelectField(choices=RANGES)

	search_field = KEYWORD
	search_type = SelectField(choices=CHOICES)
	submit_search = SubmitField('Search')

	def validate(self):
		if self.search_field == self.DATE:
			selected_date = self.search_field.data
			if not selected_date or selected_date < date.today():
				flash('Invalid date')
				return False
			else:
				return True
		else:
			return True
