from app import db
from app.models.events import Event, EventSlot
from app.models.booking import Booking
from app.models.logs import LoginHistory, LogoutHistory
from flask import redirect, url_for
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView, filters
from wtforms import StringField
from flask_admin.form.upload import ImageUploadField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Email
from app.forms.custom_validators import Interval, DateInRange
from app.views.utils import is_staff_user, is_admin_user, event_view_formatter, \
							check_slot_clash, check_event_active_slots, \
							img_filename_gen, FilterNull, FilterRegularUsers, \
							FilterStaffUsers, FilterAdminUsers
from sqlalchemy.sql import func
from datetime import date, timedelta
from pathlib import Path
from os import path


class GlobalIndexView(AdminIndexView):
	def is_accessible(self):
		return is_admin_user() or is_staff_user()

	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('staff_login'))


class StaffBaseView(ModelView):
	def is_accessible(self):
		return is_staff_user()

	def inaccessible_callback(self, name, **kwargs):
		if is_admin_user():
			return redirect(url_for('admin.index'))
		return redirect(url_for('staff_login'))


class AdminBaseView(ModelView):
	def is_accessible(self):
		return is_admin_user()

	def inaccessible_callback(self, name, **kwargs):
		if is_staff_user():
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
						 duration='Duration (H)', img_root='Image File')
	column_editable_list = ['is_launched', 'title', 'event_type', 'venue',
							'capacity', 'duration', 'price']
	column_sortable_list = ['event_id', 'has_active_slots', 'is_launched',
							'title', ('event_type', 'event_type.name'),
							('venue', 'venue.name'), 'capacity', 'duration', 'price']
	column_filters = ['is_launched', 'title', 'event_type', 'venue', 'capacity',
					  'duration', 'price', FilterNull(column=Event.img_root,
													  name='has image')]
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
							namegen=img_filename_gen)
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

				check_slot_clash(schedule, timing, slot.slot_id)
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
	column_type_formatters = event_view_formatter
	column_filters = [FilterNull(column=EventSlot.is_active, name='Active'),
					  'event', 'event_date', 'num_bookings']
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
		check_slot_clash(schedule, timing, model.slot_id)
		check_event_active_slots(model.event_id)

	# Perform data validation when deleting a slot
	def on_model_delete(self, model):
		if model.bookings:
			raise ValidationError('Cannot delete a slot that has bookings.')
		check_event_active_slots(model.event_id, sid=model.slot_id, mode='delete')


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
	column_filters = ['user.username', 'user.user_id', 'slot.event_date',
					  'slot.slot_id', 'slot.event.title', 'slot.event.event_id']
	column_filter_labels = { 'user.username' : 'username',
							 'user.user_id' : 'user id',
							 'slot.event_date' : 'event date',
							 'slot.slot_id' : 'slot id',
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
	can_delete = True
	column_display_pk = True
	column_list = ['payment_id', 'booking_id', 'booking.user',
				   'booking.slot', 'booking.quantity', 'quantity',
				   'amount', 'total_refund_qty', 'card_number']
	column_sortable_list = ['payment_id',
							'booking_id',
							('booking.user', 'booking.user.username'),
							('booking.slot', 'booking.slot.slot_id'),
							'booking.quantity',
							'quantity',
							'total_refund_qty']
	column_labels = { 'payment_id' : 'ID',
					  'booking_id' : 'Booking#',
					  'booking.user' : 'User',
					  'booking.slot' : 'Slot',
					  'booking.quantity' : 'Total BK Qty',
					  'quantity' : 'Payment Qty',
					  'total_refund_qty' : 'Refunded'}


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
	column_filters = [ 'user.username', 'admin.username',
					   FilterRegularUsers(LoginHistory.is_regular, 'user type',
										options=(('1', 'Yes'), ('0', 'No'))),
   					   FilterStaffUsers(LoginHistory.is_staff, 'user type',
										options=(('1', 'Yes'), ('0', 'No'))),
   					   FilterAdminUsers(LoginHistory.is_admin, 'user type',
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
	column_filters = [ 'user.username', 'admin.username',
					   FilterRegularUsers(LogoutHistory.is_regular, 'user type',
										options=(('1', 'Yes'), ('0', 'No'))),
   					   FilterStaffUsers(LogoutHistory.is_staff, 'user type',
										options=(('1', 'Yes'), ('0', 'No'))),
   					   FilterAdminUsers(LogoutHistory.is_admin, 'user type',
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
