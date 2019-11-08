from app import db
from app.models.users import User, Admin
from app.models.events import Event, EventSlot, EventType
from app.models.booking import Booking
from flask import flash
from sqlalchemy.sql import func
from datetime import datetime, date
from dateutil.parser import parse


def staff_user_query(name):
	user = User.query.filter(User.is_staff, User.username == name).first()
	if user is None:
		user = Admin.query.filter(Admin.username == name).first()
	return user


def query_all():
	records = db.session.query(Event.event_id, Event.title, Event.img_root)\
						.filter(Event.is_launched, Event.has_active_slots)\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.group_by(Event.event_id).order_by(Event.title).all()
	return records


def title_query(keyword):
	records = db.session.query(Event.event_id, Event.title, Event.img_root)\
						.filter(Event.is_launched, Event.has_active_slots,
								Event.title.ilike(f'%{keyword}%'))\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.group_by(Event.event_id).order_by(Event.title)\
						.order_by(Event.title).all()
	return records


def type_query(keyword):
	records = db.session.query(Event.event_id, Event.title, Event.img_root)\
						.join(EventType, Event.type_id == EventType.type_id)\
						.filter(Event.is_launched, Event.has_active_slots,
								EventType.name.ilike(f'%{keyword}%'))\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.group_by(Event.event_id).order_by(Event.title).all()
	return records


def date_query(keyword):
	records = []
	if keyword == 'None' or datetime.strptime(keyword, '%Y-%m-%d').date() < date.today():
		flash('Invalid date')
	else:
		records = db.session.query(Event.event_id, Event.title, Event.img_root)\
							.join(EventSlot, Event.event_id == EventSlot.event_id)\
							.filter(Event.is_launched, Event.has_active_slots,
									func.DATE(EventSlot.event_date) == keyword)\
							.group_by(Event.event_id).order_by(Event.title).all()

	return records


def price_query(keyword):
	records = db.session.query(Event.event_id, Event.title,
							   Event.price, Event.img_root)\
						.filter(Event.is_launched, Event.has_active_slots)\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.group_by(Event.event_id).order_by(Event.title)

	if keyword == 'free':
		records = records.filter(Event.price == 0).all()
	elif keyword == 'cheap':
		records = records.filter(Event.price < 20).all()
	elif keyword == 'mid':
		records = records.filter(Event.price >= 20, Event.price <= 50 ).all()
	else:
		records = records.filter(Event.price > 50).all()
	return records


def details_query(eid):
	return db.session.query(Event, EventSlot)\
					 .join(EventSlot, Event.event_id == EventSlot.event_id)\
					 .filter(Event.event_id == eid, Event.is_launched,
							 EventSlot.is_active)\
					 .order_by(EventSlot.event_date).all()


def event_dates_query(eid):
	return db.session.query(func.DATE(EventSlot.event_date).label('date'),
							EventSlot.vacancy.label('vacancy'))\
					 .filter(EventSlot.event_id == eid, EventSlot.is_active)\
					 .order_by(EventSlot.event_date).all()


def event_times_query(eid, date):
	return db.session.query(EventSlot.slot_id,
							func.TIME(EventSlot.event_date).label('time'),
							EventSlot.vacancy.label('vacancy'))\
					 .filter(EventSlot.event_id == eid, EventSlot.is_active,
							 func.DATE(EventSlot.event_date) == date)\
					 .order_by(EventSlot.event_date).all()


def get_event_list(search_type=None, keyword=None):
	if keyword is None:
		return query_all()
	elif search_type == 'title':
		return title_query(keyword)
	elif search_type == 'type':
		return type_query(keyword)
	elif search_type == 'date':
		return date_query(keyword)
	else:
		return price_query(keyword)


def format_events(records):
	event = { 'title' : records[0].Event.title,
			  'venue' : records[0].Event.venue,
			  'timings' : dict(),
			  'duration' : records[0].Event.duration,
			  'capacity' : records[0].Event.capacity,
			  'type': records[0].Event.event_type,
			  'desc': records[0].Event.description,
			  'price' : records[0].Event.price,
			  'img_root' : records[0].Event.img_root,
			  'event_id' : records[0].Event.event_id }

	for row in records:
		dt = parse(str(row.EventSlot.event_date))
		date = str(dt.date())
		time = str(dt.time().strftime('%H:%M'))
		vacancy = row.EventSlot.vacancy
		if date in event['timings']:
			event['timings'][date].append((time, vacancy))
		else:
			event['timings'][date] = [(time, vacancy)]

	return event


def format_bookings(records):
	records = sorted(records, key=lambda k: k.slot.event_date)

	bookings = []
	for row in records:
		dt = parse(str(row.slot.event_date))
		date = str(dt.date())
		time = str(dt.time().strftime('%H:%M'))
		bookings.append({ 'id' : row.booking_id,
						  'title' : row.slot.event.title,
						  'date' : date,
						  'time' : time,
						  'qty' : row.quantity })
	return bookings
