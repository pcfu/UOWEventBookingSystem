from app import db
from app.models.users import User, Admin
from app.models.events import Event
from flask_admin.contrib.sqla.filters import BaseSQLAFilter, FilterEmpty
from flask_admin.babel import lazy_gettext
from flask_login import current_user
from sqlalchemy.sql import literal_column
from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
from flask_admin.model import typefmt
from datetime import date, timedelta
from os import path


class FilterNull(FilterEmpty):
	def operation(self):
		return lazy_gettext('is NULL')


class FilterRegularUsers(BaseSQLAFilter):
	def apply(self, query, value, alias=None):
		if value == '1':
			return query.filter(self.column == True)
		else:
			return query.filter(self.column == False)

	def operation(self):
		return 'regular'


class FilterStaffUsers(BaseSQLAFilter):
	def apply(self, query, value, alias=None):
		if value == '1':
			return query.filter(self.column == True)
		else:
			return query.filter(self.column == False)

	def operation(self):
		return 'staff'


class FilterAdminUsers(BaseSQLAFilter):
	def apply(self, query, value, alias=None):
		if value == '1':
			return query.filter(self.column == True)
		else:
			return query.filter(self.column == False)

	def operation(self):
		return 'admin'


def is_staff_user():
	staff = None
	if current_user.is_authenticated:
		target_name = current_user.username
		staff = User.query.filter(User.is_staff, User.username == target_name).first()
	return staff is not None


def is_admin_user():
	admin = None
	if current_user.is_authenticated:
		target_name = current_user.username
		admin = Admin.query.filter(Admin.username == target_name).first()
	return admin is not None


def date_format(view, value):
    return value.strftime('%d / %b / %Y')

event_view_formatter = dict(typefmt.BASE_FORMATTERS)
event_view_formatter.update({ type(None): typefmt.null_formatter,
							  date: date_format })


# Helper Function for ImageUploadField in forms
def img_filename_gen(obj, file_data):
	idx = ''
	if obj.event_id is None:
		with db.session.no_autoflush:
			last_event = Event.query.order_by(Event.event_id.desc()).first()
		idx = f'{(last_event.event_id + 1):04}'
	else:
		idx = f'{obj.event_id:04}'

	root = 'img_eid' + idx
	obj.img_root = root
	ext = path.splitext(file_data.filename)[1]
	return secure_filename(root + ext)


def check_slot_clash(schedule, timing, id_):
	for slot in schedule:
		if slot.EventSlot.slot_id != id_:
			slot_duration = slot.Event.duration
			slot_start_time = slot.EventSlot.event_date
			slot_end_time = slot_start_time \
				+ timedelta(minutes=int(slot_duration * 60))

			error_msg =	'Slot <Date: {} | Start: {} | End: {}>'\
						' ----- clashes with ----- '\
						'Slot {} <Date: {} | Start: {} | End: {}>'\
						.format( timing[0].strftime('%Y-%m-%d'),
								 timing[0].strftime('%I:%M %p'),
								 timing[1].strftime('%I:%M %p'),
								 slot.EventSlot.slot_id,
								 slot_start_time.strftime('%Y-%m-%d'),
								 slot_start_time.strftime('%I:%M %p'),
								 slot_end_time.strftime('%I:%M %p') )

			# Raise error if new start time lies in another event slot
			if timing[0] >= slot_start_time and timing[0] < slot_end_time:
					raise ValidationError(error_msg)

			# Raise error if new end time lies in another event slot
			if timing[1] > slot_start_time and timing[1] <= slot_end_time:
					raise ValidationError(error_msg)


def check_event_active_slots(eid, sid=None, mode='edit'):
	active_slots = []
	event = Event.query.get(eid)
	for slot in event.slots:
		if mode == 'delete' and slot.slot_id != sid and slot.is_active:
			active_slots.append(slot)
		elif mode == 'edit' and slot.is_active:
			active_slots.append(slot)

	if not active_slots:
		event.is_launched = False
		db.session.commit()
