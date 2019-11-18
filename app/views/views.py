from app import db
from app.models.users import User
from app.models.events import Event, EventSlot
from app.models.payments import Payment, Promotion, EventPromotion
from app.models.logs import LoginHistory, LogoutHistory
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from wtforms import StringField
from flask_admin.form.upload import ImageUploadField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Email
from app.forms.custom_validators import Interval, DateInRange
from app.views import utils, filters
from flask_login import current_user
from flask import redirect, url_for
from sqlalchemy.sql import func
from datetime import date, timedelta
from pathlib import Path
from os import path
import math


class GlobalIndexView(AdminIndexView):
	def is_accessible(self):
		return current_user.is_authenticated and \
			(current_user.is_staff() or current_user.is_admin())

	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('login'))


class BaseView(ModelView):
	def scaffold_filters(self, name):
		filters = super().scaffold_filters(name)
		if hasattr(self, 'column_filter_labels') and name in self.column_filter_labels:
			for f in filters:
				f.name = self.column_filter_labels[name]
		return filters


class StaffBaseView(BaseView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.is_staff()

	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('login'))


class AdminBaseView(BaseView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.is_admin()


	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('login'))


class StaffVenueView(StaffBaseView):
	# List View Settings
	column_display_pk = True
	column_labels = dict(venue_id='ID')
	form_columns = [ 'name' ]


class StaffEventTypeView(StaffBaseView):
	# List View Settings
	column_display_pk = True
	column_labels = dict(type_id='ID')
	form_columns = [ 'name' ]


class StaffEventView(StaffBaseView):
	# File Paths
	par_dir = Path(__file__).parents[1]
	upload_path = path.join(par_dir, 'static/images')

	# List View Settings
	can_view_details = True
	can_set_page_size = True
	column_display_pk = True
	column_list = [ 'event_id', 'has_active_slots', 'is_launched',
					'title', 'event_type', 'venue', 'capacity',
					'duration', 'price', 'img_root' ]
	column_labels = { 'event_id' : 'ID',
					  'has_active_slots' : 'Active Slots',
					  'is_launched': 'Launched',
					  'event_type' : 'Type',
					  'duration' : 'Duration',
					  'img_root' : 'Image File' }
	column_editable_list = ['is_launched', 'title', 'event_type', 'venue',
							'capacity', 'duration', 'price']
	column_sortable_list = ['event_id', 'has_active_slots', 'is_launched',
							'title', ('event_type', 'event_type.name'),
							('venue', 'venue.name'), 'capacity', 'duration', 'price']

	def price_formatter(view, context, model, name):
		if model.price == 0.0:
			return 'FREE'
		else:
			return '${:.2f}'.format(model.price)

	def duration_formatter(view, context, model, name):
		hours = math.floor(model.duration)
		minutes = (model.duration - hours) * 60
		return '{:0>2}:{:0>2} hours'.format(hours, math.floor(minutes))

	column_formatters = {
		'price' : price_formatter,
		'duration' : duration_formatter
	}

	# Filters
	column_filters = ['is_launched', 'title', 'event_type',
					  'venue', 'capacity', 'duration', 'price',
					  filters.FilterNull(column=Event.img_root, name='has image')]
	column_filter_labels = { 'event_type' : 'Type',
							 'venue' : 'Venue' }

	# Details View Settings
	column_details_list = [ 'event_id', 'title', 'slots', 'description' ]

	# Create/Edit Form Settings
	form_extra_fields = {'path':
						 	ImageUploadField('Upload image',
							base_path=upload_path,
							thumbnail_size=(200, 200, True),
							namegen=utils.img_filename_gen)
						}
	form_columns = [ 'title', 'event_type', 'description', 'venue', 'capacity',
					 'duration', 'price', 'img_root', 'path', 'is_launched' ]
	form_args = dict(duration=dict(validators=[NumberRange(min=0.5),
											   Interval(interval=0.25)]),
					 capacity=dict(validators=[NumberRange(min=1)]),
					 price=dict(validators=[NumberRange(min=0.0)]) )
	form_widget_args = { 'img_root' : {'readonly' : True} }
	form_create_rules = [ 'title', 'event_type', 'description', 'venue', 'capacity',
						  'duration', 'price', 'img_root', 'path']
	form_edit_rules = [ 'title', 'event_type', 'description', 'venue', 'capacity',
						'duration', 'price', 'img_root', 'path', 'is_launched' ]

	# Perform data validation when creating/editing an event
	def on_model_change(self, form, model, is_created):
		if is_created:
			model.is_launched = False

		if model.has_active_slots:
			for slot in model.slots:
				new_start = slot.event_date
				new_end = new_start + timedelta(minutes=int(model.duration * 60))
				timing = (new_start, new_end)

				schedule = db.session.query(Event, EventSlot)\
							.join(EventSlot, Event.event_id == EventSlot.event_id)\
							.filter(Event.venue == model.venue)\
							.filter(func.Date(EventSlot.event_date) ==
									func.Date(new_start)).all()

				utils.check_slot_clash(schedule, timing, slot.slot_id)
		elif model.is_launched:
			raise ValidationError('Cannot launch event with no active slots.')

	# Perform data validation when deleting an event
	def on_model_delete(self, model):
		for slot in model.slots:
			if slot.bookings:
				raise ValidationError('Cannot delete event. One or more of its slots has bookings.')


class StaffEventSlotView(StaffBaseView):
	# List View Settings
	can_set_page_size = True
	column_display_pk = True
	column_list = ['slot_id', 'is_launched', 'is_active', 'event', 'event.venue',
				   'event_date', 'start_time', 'end_time', 'vacancy', 'num_bookings']
	column_labels = { 'slot_id' : 'ID',
					  'is_launched' : 'Event Launched',
					  'is_active' : 'Active',
					  'event.venue' : 'Venue',
					  'event_date' : 'Date',
					  'start_time' : 'Start',
					  'end_time' : 'End',
					  'num_bookings' : 'Bookings'}
	column_editable_list = ['is_active', 'event', 'event_date']
	column_sortable_list = ['slot_id', 'is_launched', 'is_active',
							('event', 'event.title'),
							('event.venue', 'event.venue.name'), 'event_date',
							'start_time', 'end_time', 'vacancy', 'num_bookings']

	def date_format(view, context, model, name):
		return model.event_date.strftime('%d/%b/%Y')

	column_formatters = { 'event_date' : date_format }

	# Filters
	column_filters = ['is_active', 'event.title', 'event_date', 'num_bookings']
	column_filter_labels = dict(event='Event', num_bookings='Total Bookings')
	column_filter_labels = { 'event.title' : 'Event',
							 'num_bookings' : 'Total Bookings'}

	# Create/Edit Form Settings
	form_columns = ['event', 'event_date', 'is_active']
	form_args = dict(event=dict(validators=[DataRequired()]),
 					 event_date=dict(validators=[DateInRange()]))
	form_create_rules = ['event', 'event_date']
	form_edit_rules = ['event', 'event_date', 'is_active']

	# Perform data validation when creating/editing a slot
	def on_model_change(self, form, model, is_created):
		if is_created:
			event = form.event.data
			model.is_active = True
		else:
			event = Event.query.get(model.event_id)

		start = model.event_date
		end = start + timedelta(minutes=event.duration * 60)
		timing = (start, end)
		schedule = db.session.query(Event, EventSlot)\
					.join(EventSlot, Event.event_id == EventSlot.event_id)\
					.filter(Event.venue == event.venue).all()

		# Validate promotions start dates against any changes to event last date
		# This MUST come BEFORE the next check
		last_date = event.last_active_date
		utils.check_event_promo_dates(last_date, event.promo_pairings)

		# Verify no slot clashes and deactivate event if no active slots left
		utils.check_slot_clash(schedule, timing, model.slot_id)
		utils.check_event_active_slots(event.event_id)

	# Perform data validation when deleting a slot
	def on_model_delete(self, model):
		# Validate promotions start dates against any changes to event last date
		event = Event.query.get(model.event_id)
		last_date = None
		for slot in event.slots:
			if slot.slot_id != model.slot_id and slot.is_active:
				date = slot.event_date.date()
				if not last_date or date > last_date:
					last_date = date
		utils.check_event_promo_dates(last_date, event.promo_pairings)

		# Verify no current bookings and deactivate event if no active slots left
		if model.bookings:
			raise ValidationError('Cannot delete a slot that has bookings.')
		utils.check_event_active_slots(model.event_id, sid=model.slot_id, mode='delete')


class StaffBookingView(StaffBaseView):
	# List View Settings
	can_create = False
	can_edit = False
	can_delete = False
	can_set_page_size = True
	column_display_pk = True
	column_list = ['booking_id', 'user', 'slot', 'slot.event', 'quantity']
	column_sortable_list = ['booking_id',
							('user', 'user.username'),
							('slot', 'slot.slot_id'),
							('slot.event', 'slot.event.title'),
							'quantity']
	column_labels = { 'booking_id' : 'ID',
					  'slot.event' : 'Event' }

	# Filters
	column_filters = ['user.user_id', 'user.username', 'slot.slot_id',
					  'slot.event_date', 'slot.event.event_id', 'slot.event.title']
	column_filter_labels = { 'user.user_id' : 'user id',
							 'user.username' : 'username',
							 'slot.slot_id' : 'slot id',
							 'slot.event_date' : 'slot date',
							 'slot.event.event_id' : 'event id',
							 'slot.event.title' : 'event name' }


class StaffPaymentView(StaffBaseView):
	# List View Settings
	can_create = False
	can_edit = False
	can_delete = False
	can_set_page_size = True
	column_display_pk = True
	column_list = ['payment_id', 'booking_id', 'booking.user', 'booking.slot',
				   'booking.quantity', 'quantity', 'amount', 'promotion',
				   'total_refund_qty', 'is_cancelled', 'card_number']
	column_sortable_list = [('booking.user', 'booking.user.username'),
							('booking.slot', 'booking.slot.slot_id'),
							('promotion', 'promotion.promotion_id'),
							'payment_id', 'booking_id', 'booking.quantity',
							'quantity', 'amount', 'total_refund_qty', 'is_cancelled']
	column_labels = { 'payment_id' : 'ID',
					  'booking_id' : 'Booking ID',
					  'booking.user' : 'User',
					  'booking.slot' : 'Slot',
					  'booking.quantity' : 'Booking Qty',
					  'amount' : 'Amount Paid',
					  'promotion' : 'Applied Promo',
					  'quantity' : 'Payment Qty',
					  'total_refund_qty' : 'Refund Qty',
					  'is_cancelled' : 'Cancelled' }

	def format_applied_promo(view, context, model, name):
		if not model.promotion:
			return 'NONE'
		else:
			return model.promotion

	column_formatters = {
		'amount' : lambda v, c, m, p: '${:.2f}'.format(m.amount),
		'promotion' : format_applied_promo
	}

	# Filters
	column_filters = ['booking_id', 'booking.user.username', 'booking.user.user_id',
					  'booking.slot.slot_id', 'amount', 'promotion.promo_code',
					  'promotion.promotion_id',
					  filters.BooleanFilter(column=Payment.is_cancelled,
										  name='Cancelled')]
	column_filter_labels = { 'booking.user.username' : 'username',
							 'booking.user.user_id' : 'user id',
							 'booking.slot.slot_id' : 'slot id',
							 'promotion.promo_code' : 'promo code',
							 'promotion.promotion_id' : 'promotion id'}


class StaffRefundView(StaffBaseView):
	# List View Settings
	can_create = False
	can_edit = False
	can_delete = False
	can_set_page_size = True
	column_display_pk = True
	column_list = ['refund_id', 'payment', 'quantity', 'refund_amount']
	column_sortable_list = ['refund_id', ('payment', 'payment.payment_id'),
							'quantity', 'refund_amount']
	column_labels = {'refund_id' : 'ID',
					 'quantity' : 'Refund Qty'}
	column_formatters = {
		'refund_amount' : lambda v, c, m, p: '${:.2f}'.format(m.refund_amount)
	}

	# Filters
	column_filters = ['payment.payment_id', 'payment.booking_id', 'refund_amount']
	column_filter_labels = { 'payment.payment_id' : 'payment id',
							 'payment.booking_id' : 'booking id' }


class StaffPromotionView(StaffBaseView):
	# List View Settings
	can_view_details = True
	can_set_page_size = True
	column_display_pk = True
	column_list = ['promotion_id', 'promo_code', 'promo_percentage', 'date_start',
				   'date_end', 'has_active_event_promo', 'is_used', 'events_last_date']
	column_labels = { 'promotion_id' : 'ID',
					  'promo_code' : 'Code',
					  'promo_percentage' : 'Discount',
					  'date_start' : 'Start Date',
					  'date_end' : 'End Date',
					  'has_active_event_promo' : 'Has Active EP',
					  'is_used' : 'Used'}
	column_sortable_list = ['promotion_id', 'promo_code', 'promo_percentage',
							'date_start', 'date_end', 'has_active_event_promo', 'is_used']

	def get_last_dates(view, context, model, name):
		data = []
		for ep in [ep for ep in model.event_pairings if ep.is_active]:
			last_date = ep.event.last_active_date
			if last_date is None:
				data.append('{} [{}]'.format(ep.event.title, last_date))
			else:
				data.append('{} [{}]'.format(ep.event.title, last_date.strftime('%d/%b/%Y')))
		return data

	column_formatters = {
		'promo_percentage' : lambda v, c, m, p: '{}%'.format(m.promo_percentage),
		'date_start' : lambda v, c, m, p: m.date_start.strftime('%d/%b/%Y'),
		'date_end' : lambda v, c, m, p: m.date_end.strftime('%d/%b/%Y'),
		'events_last_date' : get_last_dates
	}

	# Details View Settings
	column_details_list = [ 'promotion_id', 'promo_code', 'payments', 'event_pairings']
	column_details_labels = { 'event_pairings' : 'events' }

	# Filters
	column_filters = ['promo_percentage',
					  filters.BooleanFilter(column=Promotion.has_active_event_promo,
										  name='Has Active EP'),
					  filters.BooleanFilter(column=Promotion.is_used, name='Is Used')]
	column_filter_labels = { 'promo_percentage' : 'discount',
							 'is_used' : 'is used'}

	# Create/Edit form settings
	form_rules = ['promo_code', 'promo_percentage', 'date_start', 'date_end']
	form_args = dict(promo_percentage=dict(validators=[NumberRange(min=1, max=100,
										message='Discount must be between 1 - 100.')]))

	# Perform data validation when creating/editing a promotion
	def on_model_change(self, form, model, is_created):
		if model.date_end <= date.today():
			raise ValidationError('End date must be later than current date.')
		elif model.date_start > model.date_end:
			raise ValidationError('Start date must be earlier than end date.')

		if not is_created:
			if model.is_used and form.promo_percentage.object_data != form.promo_percentage.data:
				raise ValidationError('Cannot change discount value for promotions applied by users.')

			# Check updated record's start date not later than associated event's last active date
			if model.has_active_event_promo:
				promo_start_date = model.date_start
				for ep in [ep for ep in model.event_pairings if ep.is_active]:
					event_last_date = ep.event.last_active_date
					if event_last_date is not None and promo_start_date > event_last_date:
						msg = 'Promotion applicable to [ {} ] '.format(ep.event.title)
						msg += 'but effective start date [ {} ] '.format(promo_start_date)
						msg += 'not before last day of event [ {} ].'.format(event_last_date)
						raise ValidationError(msg)

	# Perform data validation when deleting a promotion
	def on_model_delete(self, model):
		if model.is_used:
			raise ValidationError('Cannot delete promotions applied by users.')


class StaffEventPromoView(StaffBaseView):
	# List View Settings
	can_set_page_size = True
	column_list = ['event', 'promotion', 'event.last_active_date',
				   'promotion.date_start', 'promotion.date_end', 'is_active']
	column_labels = {'event.last_active_date' : 'Event End',
					 'promotion.date_start' : 'Promo Start',
					 'promotion.date_end' : 'Promo End',
					 'is_active' : 'Active'}
	column_sortable_list = [ ('event', 'event.event_id'),
							 ('promotion', 'promotion.promotion_id'),
							 'event.last_active_date',
							 'promotion.date_start',
							 'promotion.date_end',
							 'is_active' ]

	def get_last_date(view, context, model, name):
		if model.event.last_active_date:
			last_date = model.event.last_active_date.strftime('%d/%b/%Y')
		else:
			last_date = 'None'
		return last_date

	column_formatters = {
		'event.last_active_date' : get_last_date,
		'promotion.date_start' :
			lambda v, c, m, p: m.promotion.date_start.strftime('%d/%b/%Y'),
		'promotion.date_end' :
			lambda v, c, m, p: m.promotion.date_end.strftime('%d/%b/%Y'),
	}

	# Filters
	column_filters = ['event.title',
					  'event.last_active_date',
					  'promotion.promo_code',
					  'promotion.date_start',
					  'promotion.date_end',
					  filters.BooleanFilter(column=EventPromotion.is_active,
										  name='Is Active')]
	column_filter_labels = { 'event.title' : 'Event Title',
							 'event.last_active_date' : 'Event End',
							 'promotion.promo_code' : 'Promo Code'}

	# Perform data validation when creating/editing an event promotion
	def on_model_change(self, form, model, is_created):
		if model.is_active:
			event_last_date = model.event.last_active_date
			promo_start_date = model.promotion.date_start
			if event_last_date is not None and event_last_date < promo_start_date:
				msg = 'Promotion applicable to [ {} ] '.format(model.event.title)
				msg += 'but effective start date [ {} ] '.format(promo_start_date)
				msg += 'not before last day of event [ {} ].'.format(event_last_date)
				raise ValidationError(msg)


class AdminUserView(AdminBaseView):
	# List View Settings
	can_set_page_size = True
	column_display_pk = True
	column_list = ['user_id', 'username', 'email', 'group.group_name']
	column_labels = {'user_id' : 'ID',
					 'group.group_name' : 'Usergroup'}
	column_sortable_list = [ 'user_id', 'username', 'email', 'group.group_name']

	# Filters
	column_filters = [ 'user_id', 'username',
					   filters.RegularUserFilter(User.group_id, 'Usergroup',
												 options=(('1', 'Yes'), ('0', 'No'))),
					   filters.StaffUserFilter(User.group_id, 'Usergroup',
											   options=(('1', 'Yes'), ('0', 'No'))),
					   filters.AdminUserFilter(User.group_id, 'Usergroup',
											   options=(('1', 'Yes'), ('0', 'No')))	]

	# Create/Edit Form Settings
	form_extra_fields = { 'password' : StringField('Password', validators=[DataRequired()]),
						  'change_password': StringField('Change Password') }
	form_columns = ['group', 'username', 'email', 'password',
					'change_password', 'password_hash']
	form_args = dict(email=dict(validators=[DataRequired(), Email()]))
	form_widget_args = { 'password_hash' : {'readonly' : True} }
	form_create_rules = ['group', 'username', 'email', 'password']
	form_edit_rules = ['group', 'username', 'email', 'change_password',
					   'password_hash']

	# Perform data validation when creating/editing a user
	def on_model_change(self, form, model, is_created):
		if is_created:
			model.set_password(form.password.data)
		else:
			if model == current_user and form.group.data.group_name != 'admin':
				raise ValidationError('Cannot revoke admin privilege from self')

			if form.change_password.data:
				model.set_password(form.change_password.data)

	# Perform data validation when deleting a user
	def on_model_delete(self, model):
		if model == current_user:
			raise ValidationError('Cannot delete self')


class AdminLoginHistoryView(AdminBaseView):
	# List View Settings
	can_create = False
	can_edit = False
	can_delete = False
	can_set_page_size = True
	column_display_pk = True
	column_list = ['in_id', 'timestamp', 'user', 'user.group']
	column_labels = { 'in_id' : 'ID',
					  'user.group' : 'Usergroup' }
	column_sortable_list = ['in_id', 'timestamp',
							('user', 'user.username'),
							('user.group', 'user.group.group_name')]

	# Filters
	column_filters = [ 'user.user_id', 'user.username', 'user.group.group_name' ]
	column_filter_labels = {'user.user_id' : 'User ID',
							'user.username' : 'Username',
							'user.group.group_name' : 'User Group'}


class AdminLogoutHistoryView(AdminBaseView):
	# List View Settings
	can_create = False
	can_edit = False
	can_delete = False
	can_set_page_size = True
	column_display_pk = True
	column_list = ['out_id', 'timestamp', 'user', 'user.group']
	column_labels = { 'out_id' : 'ID',
					  'user.group' : 'Usergroup' }
	column_sortable_list = ['out_id', 'timestamp',
							('user', 'user.username'),
							('user.group', 'user.group.group_name')]

	# Filters
	column_filters = [ 'user.user_id', 'user.username', 'user.group.group_name' ]
	column_filter_labels = {'user.user_id' : 'User ID',
							'user.username' : 'Username',
							'user.group.group_name' : 'User Group'}
