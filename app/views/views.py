from app import db
from app.models.events import Event, EventSlot
from flask import redirect, url_for
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from app.forms.custom_validators import Interval, DateInRange
from app.views.utils import is_staff_user, is_admin_user, event_view_formatter, \
							check_slot_clash, img_filename_gen
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
	column_list = [ 'event_id', 'is_scheduled', 'is_launched',
					'title', 'event_type', 'venue', 'capacity',
					'duration', 'price', 'img_root' ]
	column_labels = dict(is_scheduled='Scheduled', is_launched='Launched',
						 event_id='ID', event_type='Type',
						 duration='Duration (H)', img_root='Image File')
	column_editable_list = ( 'is_launched', 'title', 'event_type', 'venue',
							 'capacity', 'duration', 'price' )
	column_sortable_list = [ 'event_id', 'is_scheduled', 'is_launched', 'title' ]

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


	# Perform data validation when creating/editing an event
	def on_model_change(self, form, model, is_created):
		if model.is_scheduled:
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
			raise ValidationError('Cannot launch unscheduled event.')


class StaffEventSlotView(StaffBaseView):
	# List View Settings
	can_view_details = True
	can_set_page_size = True
	column_display_pk = True
	column_list = [ 'slot_id', 'is_launched', 'event',
					'event_date', 'start_time', 'end_time' ]
	column_labels = dict(slot_id='ID', is_launched='Launched',
						 event_date='Date', start_time='Start', end_time='End')
	column_sortable_list = ( 'slot_id', ('event', 'event.title'), 'event_date')
	column_type_formatters = event_view_formatter

	# Details View Settings
	column_details_list = [ 'slot_id', 'event', 'event_date' ]

	# Create/Edit Form Settings
	form_args = dict( event=dict(validators=[DataRequired()]),
					  event_date=dict(validators=[DateInRange()]) )

	# Perform data validation when creating/editing a slot
	def on_model_change(self, form, model, is_created):
		duration = form.event.data.duration
		new_start = model.event_date
		new_end = new_start + timedelta(minutes=duration * 60)
		timing = (new_start, new_end)

		new_venue = form.event.data.venue
		schedule = db.session.query(Event, EventSlot)\
					.join(EventSlot, Event.event_id == EventSlot.event_id)\
					.filter(Event.venue == new_venue).all()

		check_slot_clash(schedule, timing, model.slot_id)


class StaffBookingView(StaffBaseView):
	can_create = False
	can_edit = False
	can_delete = False
	column_display_pk = True


class AdminUserView(AdminBaseView):
	# List View Settings
	column_display_pk = True
	column_labels = dict(user_id='ID')
	column_exclude_list = ['password_hash']
