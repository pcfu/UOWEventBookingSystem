from flask_wtf import FlaskForm
from app import db, query
from app.models.users import User, Admin
from app.models.events import Event, EventSlot
from app.models.payments import EventPromotion, Promotion
from wtforms import FormField, StringField, PasswordField, BooleanField, HiddenField,\
					SubmitField, IntegerField, SelectField, DecimalField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, EqualTo, ValidationError, \
								NumberRange, Email, Optional
from wtforms_components import NumberInput
from flask_login import current_user
from app.views.utils import is_admin_user
from sqlalchemy.sql import func
from app.query import staff_user_query
from datetime import date, datetime
import re


def RaiseError(field, message='Invalid data'):
	error_list = list(field.errors)
	error_list.append(message)
	field.errors = tuple(error_list)


class BaseLogin(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

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


class UpdateEmailForm(FlaskForm):
	email = StringField('New Email', validators=[Email()])
	update_email = SubmitField('Update')

	def validate_email(self, email):
		if email.data == current_user.email:
			raise ValidationError('You are already using this email')

		if is_admin_user():
			user = Admin.query.filter(Admin.email == email.data).first()
		else:
			user = User.query.filter(User.email == email.data).first()
		if user is not None:
			raise ValidationError('Email already taken')


class UpdatePasswordForm(FlaskForm):
	old_password = PasswordField('Old Password')
	new_password = PasswordField('New Password')
	confirm_password = PasswordField('Confirm Password')
	update_password = SubmitField('Update')

	def validate(self):
		# Check old password
		if not current_user.check_password(self.old_password.data):
			RaiseError(self.old_password, message='Incorrect password')
			return False

		# Check new password
		if re.search(r'\s', self.new_password.data):
			RaiseError(self.new_password,
					   message='Password must not contain any whitespaces')
			return False
		if self.new_password.data == self.old_password.data:
			RaiseError(self.new_password,
					   message='New password must be different from old password')
			return False

		# Check confirm password
		if self.new_password.data != self.confirm_password.data:
			RaiseError(self.confirm_password, message='Passwords must match')
			return False
		return True


class AccountUpdateForm(FlaskForm):
	update_email = FormField(UpdateEmailForm)
	update_password = FormField(UpdatePasswordForm)


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
	vacancy = StringField(render_kw={'readonly':'True'})
	count = IntegerField('Count', default=1,
						 validators=[DataRequired(), NumberRange(min=1)],
						 widget=NumberInput())
	price = DecimalField('Price', render_kw={'readonly':'True'}, places=2)
	submit = SubmitField('Book')

	def preload(self, user, event):
		self.title.data = event.title
		self.username.data = user.username

		# Get dates
		date_records = query.event_dates_query(event.event_id)
		date_list = []
		for rec in date_records:
			if rec.date not in date_list and rec.vacancy > 0:
				date_list.append(rec.date)
				self.dates.choices.append((rec.date, rec.date))
		self.dates.data = date_list[0]	#set first item as pre-selected default

		# Get timings for pre-selected date
		timings = query.event_times_query(event.event_id, self.dates.data)
		for timing in timings:
			if timing.vacancy > 0:
				self.times.choices.append((timing.slot_id, timing.time))

		default_slot_id = self.times.choices[0][0]
		self.vacancy.data = EventSlot.query.get(default_slot_id).vacancy
		self.price.data = event.price
		self.capacity = event.capacity


class PromotionForm(FlaskForm):
	promo_code = StringField('Promotion Code')
	promo_event_id = IntegerField()
	skip_promo_check = HiddenField(default='NOSKIP')
	current_code_applied = HiddenField(default='NONE')
	apply_promo = SubmitField('Apply')

	def validate_promo_code(self, promo_code):
		if self.skip_promo_check.data == 'SKIP':
			return True
		else:
			code = self.promo_code.data
			promotion = Promotion.query.filter_by(promo_code=code).first()
			if promotion is None:
				raise ValidationError('Invalid promo code')

			eid = self.promo_event_id.data
			ep = EventPromotion.query.filter_by(is_active=True, event_id=eid,
												promotion_id=promotion.promotion_id).first()
			if not ep:
				raise ValidationError('Promo code not applicable for this event')
			elif ep.promotion.dt_start > datetime.now():
				raise ValidationError('Promotion is not active yet')
			elif ep.promotion.dt_end < datetime.now():
				raise ValidationError('Promotion expired')


class PaymentForm(FlaskForm):
	card_number = IntegerField('Card Number', validators=[DataRequired()])
	name_on_card = StringField('Name on card', validators=[DataRequired()])
	expire_month = IntegerField('Expiry Date', validators=[DataRequired()],
								render_kw={'placeholder':'MM'})
	expire_year = IntegerField(validators=[DataRequired()],
							   render_kw={'placeholder':'YY'})
	cvv = IntegerField('CVV', validators=[DataRequired()])
	address = StringField('Billing Address', validators=[Optional()])
	postal_code = IntegerField('Postal Code', validators=[Optional()],
							   render_kw={'placeholder':'i.e. 599491'})
	contact = IntegerField('Contact Number', validators=[Optional()])
	promo = FormField(PromotionForm)
	submit = SubmitField('Pay')

	def validate_card_number(self, card_number):
		if len(str(card_number.data)) < 14 or len(str(card_number.data)) > 16:
			raise ValidationError('Invalid card number!')

	def validate_name_on_card(self, name_on_card):
		pattern = '[\d!@#$%^&*_+=]' #pattern allows hyphens in names
		if re.search(pattern, name_on_card.data):
			raise ValidationError('Invalid name!')

	def validate_expire_month(self, expire_month):
		if expire_month.data < 1 or expire_month.data > 12:
			raise ValidationError('Invalid month!')

	def validate_expire_year(self, expire_year):
		if (expire_year.data > int(datetime.now().strftime("%y")) + 5) or \
		(expire_year.data < int(datetime.now().strftime("%y"))) or (expire_year.data < 1):
			raise ValidationError('Invalid year!')


	''' temporarily disabled because postal codes and numbers may not be local

	def validate_postal_code(self, postal_code):
		if postal_code is not None:
			if not len(str(postal_code.data)) == 6:
				raise ValidationError('Invalid postal code!' + len(postal_code.data))

	def validate_contact(self, contact):
		if contact is not None:
			if not len(str(contact.data)) == 8:
				raise ValidationError('Invalid contact number')
	'''
