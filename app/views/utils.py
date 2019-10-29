from app.query import staff_user_query
from app.models.users import User, Admin
#from app.models.events import Event
from flask_login import current_user
from sqlalchemy.sql import literal_column
#from werkzeug.utils import secure_filename
#from wtforms.validators import ValidationError
#from flask_admin.model import typefmt
#from datetime import date, timedelta
#from os import path


'''
def date_format(view, value):
    return value.strftime('%d / %b / %Y')

event_view_formatter = dict(typefmt.BASE_FORMATTERS)
event_view_formatter.update({ type(None): typefmt.null_formatter,
							  date: date_format })
'''


def is_staff_user():
	staff = None
	if current_user.is_authenticated:
		target_name = current_user.username
		staff = staff_user_query(target_name)
	return staff is not None


'''
event_venue_choices = [ ('room1', 'Room 1'),
					  	('room2', 'Room 2'),
					  	('room3', 'Room 3'),
						('room4', 'Room 4'),
						('room5', 'Room 5'),
						('hall1', 'Hall 1'),
						('hall2', 'Hall 2'),
						('auditorium', 'Auditorium') ]


event_type_choices = [ ('lecture', 'Lecture'),
					   ('seminar', 'Seminar'),
			  		   ('conference', 'Conference'),
					   ('workshop', 'Workshop'),
					   ('talk', 'Talk'),
					   ('networking', 'Networking'),
					   ('party', 'Party'),
					   ('concert', 'Concert') ]


# Helper Function for ImageUploadField in forms
def img_filename_gen(obj, file_data):
	idx = ''
	if obj.event_id is None:
		last_event = Event.query.order_by(Event.event_id.desc()).first()
		idx = f'{(last_event.event_id):04}'
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
'''
