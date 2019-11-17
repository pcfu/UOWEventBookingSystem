from flask_wtf import FlaskForm
from app import db_tools
from app.models.users import User
from app.models.events import EventType, EventSlot #, Event
from app.models.payments import Payment, Promotion #, EventPromotion
from wtforms import FormField, StringField, PasswordField, \
					BooleanField, IntegerField, DecimalField, \
					SelectField, SubmitField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError, Email, \
							   EqualTo, NumberRange, Optional
from wtforms_components import NumberInput
#from flask_login import current_user
from datetime import date, datetime
import re


def RaiseError(field, message='Invalid data'):
	error_list = list(field.errors)
	error_list.append(message)
	field.errors = tuple(error_list)


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

	def validate(self):
		user = User.query.filter_by(username=self.username.data).first()
		if user is None:
			RaiseError(self.username, message='Invalid username')
			return False
		if not user.check_password(self.password.data):
			RaiseError(self.password, message='Incorrect password')
			return False
		return True


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


'''
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
'''


class DateRangeForm(FlaskForm):
	from_date = DateField(default=date.today(), label='From')
	to_date = DateField(default=date.today(), label='To')


class SearchForm(FlaskForm):
	CHOICES = [('title', 'Title'),
			   ('date', 'Date'),
			   ('type', 'Type' ),
			   ('price', 'Price')]
	RANGES = [('free', 'FREE'),
			  ('cheap', '< $20'),
			  ('mid', '$20 - 50'),
			  ('expensive', '> $50')]
	CATEGORIES = [(row.name, row.name) for row in EventType.query.all()]

	STRING_FIELD = StringField()
	DATE_FIELD = FormField(DateRangeForm)
	PRICE_FIELD = SelectField(choices=RANGES)
	TYPE_FIELD = SelectField(choices=CATEGORIES, coerce=str)

	search_field = STRING_FIELD
	search_type = SelectField(choices=CHOICES)
	submit_search = SubmitField('Search')

	def validate(self):
		if self.search_field == self.DATE_FIELD:
			from_date = self.search_field.data['from_date']
			to_date = self.search_field.data['to_date']

			if from_date is None or to_date is None:
				RaiseError(self.DATE_FIELD.from_date, message='Invalid date(s)')
				return False
			elif from_date > to_date:
				RaiseError(self.DATE_FIELD.from_date,
					   message='End date cannot be earlier than start date')
				return False
		return True


class BookingForm(FlaskForm):
	title = StringField(render_kw={'readonly':'True'})
	username = StringField(render_kw={'readonly':'True'})
	date = SelectField(choices=[])
	time = SelectField(choices=[])
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
		date_records = db_tools.event_dates_query(event.event_id)
		date_list = []
		for rec in date_records:
			if rec.date not in date_list and rec.vacancy > 0:
				date_list.append(rec.date)
				text = datetime.strptime(rec.date, '%Y-%m-%d').strftime('%d/%m/%y')
				self.date.choices.append((rec.date, text))

				#self.date.choices.append((rec.date, rec.date.strftime('%d/%b/%Y')))
		self.date.data = date_list[0]	#set first item as pre-selected default

		# Get timings for pre-selected date
		timings = db_tools.event_times_query(event.event_id, self.date.data)
		for timing in timings:
			if timing.vacancy > 0:
				text = datetime.strptime(timing.time, '%H:%M:%S')\
							   .strftime('%-I:%M %p')
				self.time.choices.append((timing.slot_id, text))

		default_slot_id = self.time.choices[0][0]
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
			elif ep.promotion.date_start > date.today():
				raise ValidationError('Promotion is not active yet')
			elif ep.promotion.date_end < date.today():
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
