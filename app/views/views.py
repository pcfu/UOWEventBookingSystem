from app import db
from app.models.events import Event, EventSlot
from app.models.payments import Payment
from app.models.booking import Booking
from app.models.logs import LoginHistory, LogoutHistory
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView, filters
from wtforms import StringField
from flask_admin.form.upload import ImageUploadField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Email
from app.forms.custom_validators import Interval, DateInRange
from app.views import utils
from flask import redirect, url_for
from sqlalchemy.sql import func
from datetime import date, timedelta
from pathlib import Path
from os import path
import math


class GlobalIndexView(AdminIndexView):
	def is_accessible(self):
		return utils.is_admin_user() or utils.is_staff_user()

	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('staff_login'))


class StaffBaseView(ModelView):
	def is_accessible(self):
		return utils.is_staff_user()

	def inaccessible_callback(self, name, **kwargs):
		if utils.is_admin_user():
			return redirect(url_for('admin.index'))
		return redirect(url_for('staff_login'))


class AdminBaseView(ModelView):
	def is_accessible(self):
		return utils.is_admin_user()

	def inaccessible_callback(self, name, **kwargs):
		if utils.is_staff_user():
			return redirect(url_for('admin.index'))
		return redirect(url_for('staff_login'))


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
	column_labels = dict(has_active_slots='Active Slots', is_launched='Launched',
						 event_id='ID', event_type='Type',
						 duration='Duration', img_root='Image File')
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
					  utils.FilterNull(column=Event.img_root, name='has image')]
	column_filter_labels = dict(event_type='Type', venue='Venue')

	def scaffold_filters(self, name):
		filters = super().scaffold_filters(name)
		if name in self.column_filter_labels:
			for f in filters:
				f.name = self.column_filter_labels[name]
		return filters

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
	column_filters = ['is_active', 'event', 'event_date', 'num_bookings']
	column_filter_labels = dict(event='Event', num_bookings='Total Bookings')

	def scaffold_filters(self, name):
		filters = super().scaffold_filters(name)
		if name in self.column_filter_labels:
			for f in filters:
				f.name = self.column_filter_labels[name]
		return filters

	# Create/Edit Form Settings
	form_columns = ['event', 'event_date', 'is_active']
	form_args = dict(event=dict(validators=[DataRequired()]),
 					 event_date=dict(validators=[DateInRange()]))
	form_create_rules = ['event', 'event_date']
	form_edit_rules = ['event', 'event_date', 'is_active']

	# Perform data validation when creating/editing a slot
	def on_model_change(self, form, model, is_created):
		if is_created:
			duration = form.event.data.duration
			new_venue = form.event.data.venue
			model.is_active = True
		else:
			event = Event.query.get(model.event_id)
			duration = event.duration
			new_venue = event.venue

		new_start = model.event_date
		new_end = new_start + timedelta(minutes=duration * 60)
		timing = (new_start, new_end)

		schedule = db.session.query(Event, EventSlot)\
					.join(EventSlot, Event.event_id == EventSlot.event_id)\
					.filter(Event.venue == new_venue).all()
		utils.check_slot_clash(schedule, timing, model.slot_id)
		utils.check_event_active_slots(model.event_id)

	# Perform data validation when deleting a slot
	def on_model_delete(self, model):
		if model.bookings:
			raise ValidationError('Cannot delete a slot that has bookings.')
		utils.check_event_active_slots(model.event_id, sid=model.slot_id, mode='delete')


class StaffBookingView(StaffBaseView):
	# List View Settings
	can_create = False
	can_edit = False
	can_delete = False
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
	column_filters = ['user.username', 'user.user_id', 'slot.slot_id',
					  'slot.event_date', 'slot.event.title', 'slot.event.event_id']
	column_filter_labels = { 'user.username' : 'username',
							 'user.user_id' : 'user id',
							 'slot.slot_id' : 'slot id',
							 'slot.event_date' : 'event date',
							 'slot.event.title' : 'event name',
							 'slot.event.event_id' : 'event id'}

	def scaffold_filters(self, name):
		filters = super().scaffold_filters(name)
		if name in self.column_filter_labels:
			for f in filters:
				f.name = self.column_filter_labels[name]
		return filters


class StaffPaymentView(StaffBaseView):
	# List View Settings
	can_create = False
	can_edit = False
	can_delete = False
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
					  utils.BooleanFilter(column=Payment.is_cancelled,
										  name='Cancelled')]
	column_filter_labels = { 'booking.user.username' : 'username',
							 'booking.user.user_id' : 'user id',
							 'booking.slot.slot_id' : 'slot id',
							 'promotion.promo_code' : 'promo code',
							 'promotion.promotion_id' : 'promotion id'}

	def scaffold_filters(self, name):
		filters = super().scaffold_filters(name)
		if name in self.column_filter_labels:
			for f in filters:
				f.name = self.column_filter_labels[name]
		return filters


class StaffRefundView(StaffBaseView):
	# List View Settings
	can_create = False
	can_edit = False
	can_delete = False
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

	def scaffold_filters(self, name):
		filters = super().scaffold_filters(name)
		if name in self.column_filter_labels:
			for f in filters:
				f.name = self.column_filter_labels[name]
		return filters


class AdminUserView(AdminBaseView):
	# List View Settings
	column_display_pk = True
	column_labels = dict(user_id='ID')
	column_exclude_list = ['password_hash']

	# Create/Edit Form Settings
	form_extra_fields =	{'password' : StringField('Password',
												  validators=[DataRequired()]),
						 'change_password': StringField('Change Password')}
	form_columns = ['username', 'email', 'password', 'change_password',
					'password_hash', 'is_staff']
	form_args = dict(email=dict(validators=[DataRequired(), Email()]))
	form_widget_args = { 'password_hash' : {'readonly' : True} }
	form_create_rules = ['username', 'email', 'password', 'is_staff']
	form_edit_rules = ['username', 'email', 'change_password',
					   'password_hash', 'is_staff']

	# Perform data validation when creating/editing a slot
	def on_model_change(self, form, model, is_created):
		if is_created:
			model.set_password(form.password.data)
		else:
			if form.change_password.data:
				model.set_password(form.change_password.data)


class AdminLoginHistoryView(AdminBaseView):
	# List View Settings
	can_create = False
	can_edit = False
	column_display_pk = True
	column_labels = dict(in_id='ID')
	column_list = ['in_id', 'timestamp', 'user', 'admin']
	column_sortable_list = ['in_id', 'timestamp',
							('user', 'user.username'),
							('admin', 'admin.username')]

	# Filters
	column_filters = [ 'user.username', 'admin.username',
					   utils.FilterRegularUsers(LoginHistory.is_regular, 'user type',
												options=(('1', 'Yes'), ('0', 'No'))),
   					   utils.FilterStaffUsers(LoginHistory.is_staff, 'user type',
											  options=(('1', 'Yes'), ('0', 'No'))),
   					   utils.FilterAdminUsers(LoginHistory.is_admin, 'user type',
											  options=(('1', 'Yes'), ('0', 'No')))
					]
	column_filter_labels = {'user.username' : 'user name',
							'admin.username' : 'admin name'}

	def scaffold_filters(self, name):
		filters = super().scaffold_filters(name)
		if name in self.column_filter_labels:
			for f in filters:
				f.name = self.column_filter_labels[name]
		return filters


class AdminLogoutHistoryView(AdminBaseView):
	# List View Settings
	can_create = False
	can_edit = False
	column_display_pk = True
	column_labels = dict(out_id='ID')
	column_list = ['out_id', 'timestamp', 'user', 'admin']
	column_sortable_list = ['out_id', 'timestamp',
							('user', 'user.username'),
							('admin', 'admin.username')]

	# Filters
	column_filters = [ 'user.username', 'admin.username',
					   utils.FilterRegularUsers(LogoutHistory.is_regular, 'user type',
												options=(('1', 'Yes'), ('0', 'No'))),
   					   utils.FilterStaffUsers(LogoutHistory.is_staff, 'user type',
											  options=(('1', 'Yes'), ('0', 'No'))),
   					   utils.FilterAdminUsers(LogoutHistory.is_admin, 'user type',
											  options=(('1', 'Yes'), ('0', 'No')))
					]
	column_filter_labels = {'user.username' : 'user name',
							'admin.username' : 'admin name'}

	def scaffold_filters(self, name):
		filters = super().scaffold_filters(name)
		if name in self.column_filter_labels:
			for f in filters:
				f.name = self.column_filter_labels[name]
		return filters
