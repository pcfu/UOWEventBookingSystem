from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,\
					SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError
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
	choices = [('title', 'Title'),
			   ('date', 'Date'),
			   ('time', 'Time'),
			   ('type', 'Type' ),
			   ('price', 'Price')]
	search_type = SelectField(choices=choices)
	keyword = StringField('')
	search = SubmitField('Search')
