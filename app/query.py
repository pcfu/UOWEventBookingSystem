from app import db
from app.models.users import User, Admin
from app.models.events import Event, EventSlot, EventType
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
						.filter(Event.is_launched)\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.group_by(Event.event_id).order_by(Event.title).all()
	return records


def title_query(keyword):
	records = db.session.query(Event.event_id, Event.title, Event.img_root)\
						.filter(Event.is_launched, Event.title.ilike(f'%{keyword}%'))\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.group_by(Event.event_id).order_by(Event.title)\
						.order_by(Event.title).all()
	return records


def type_query(keyword):
	records = db.session.query(Event.event_id, Event.title, Event.img_root)\
						.join(EventType, Event.type_id == EventType.type_id)\
						.filter(Event.is_launched,
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
							.filter(Event.is_launched,
									func.DATE(EventSlot.event_date) == keyword)\
							.group_by(Event.event_id).order_by(Event.title).all()

	return records


def price_query(keyword):
	records = db.session.query(Event.event_id, Event.title,
							   Event.price, Event.img_root)\
						.filter(Event.is_launched)\
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


def format_events(records):
	common = records.first()
	event = { 'title' : common.Event.title,
			  'venue' : common.Event.venue,
			  'timings' : dict(),
			  'duration' : common.Event.duration,
			  'capacity' : common.Event.capacity,
			  'type': common.Event.event_type,
			  'desc': common.Event.description,
			  'price' : common.Event.price,
			  'img_root' : common.Event.img_root,
			  'event_id' : common.Event.event_id }

	for row in records.all():
		dt = parse(str(row.EventSlot.event_date))
		date = str(dt.date())
		time = str(dt.time().strftime('%H:%M'))

		if date in event['timings']:
			event['timings'][date].append(time)
		else:
			event['timings'][date] = [time]

	return event
