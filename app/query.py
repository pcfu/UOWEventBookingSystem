from app import db
from app.models import Event, EventSlot
from flask import flash
from sqlalchemy.sql import func
from datetime import datetime, date


def query_all():
	records = db.session.query(Event.event_id, Event.event_title, Event.img_root)\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.group_by(Event.event_id).order_by(Event.event_title).all()
	return records


def title_query(keyword):
	records = db.session.query(Event.event_id, Event.event_title, Event.img_root)\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.group_by(Event.event_id).order_by(Event.event_title)\
						.filter(Event.event_title.ilike(f'%{keyword}%'))\
						.order_by(Event.event_title).all()
	return records


def type_query(keyword):
	records = db.session.query(Event.event_id, Event.event_title,
							   Event.event_type, Event.img_root)\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.group_by(Event.event_id).order_by(Event.event_title)\
						.filter(Event.event_type.ilike(f'%{keyword}%'))\
						.order_by(Event.event_title).all()
	return records


def date_query(keyword):
	records = []
	if keyword == 'None' or datetime.strptime(keyword, '%Y-%m-%d').date() < date.today():
		flash('Invalid date')
	else:
		records = db.session.query(Event.event_id, Event.event_title,
								   EventSlot.event_date, Event.img_root)\
							.join(EventSlot, Event.event_id == EventSlot.event_id)\
							.filter(func.DATE(EventSlot.event_date) == keyword)\
							.group_by(Event.event_id)\
							.order_by(Event.event_title).all()
	return records


def price_query(keyword):
	records = db.session.query(Event.event_id, Event.event_title,
								   Event.price, Event.img_root)\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.group_by(Event.event_id).order_by(Event.event_title)

	if keyword == 'free':
		records = records.filter(Event.price == 0).all()
	elif keyword == 'cheap':
		records = records.filter(Event.price < 20).all()
	elif keyword == 'mid':
		records = records.filter(Event.price >= 20, Event.price <= 50 ).all()
	else:
		records = records.filter(Event.price > 50).all()
	return records



### DO NOT DELETE THESE. Future reference for event detail queries
'''
def format_events(records):
	event_list = []

	event = dict()
	for row in records:
		dt = parse(str(row.EventSlot.event_date))
		date = str(dt.date())
		time = str(dt.time().strftime('%H:%M'))

		if not bool(event) or row.Event.event_id != event['event_id']:
			add_to_list(event_list, event)
			event = { 'title' : row.Event.event_title,
					  'venue' : row.Event.venue,
					  'dates' : { date },
					  'times' : { time },
					  'duration' : row.Event.duration,
					  'capacity' : row.Event.capacity,
					  'type': row.Event.event_type,
					  'desc': row.Event.description,
					  'price' : row.Event.price,
					  'event_id' : row.Event.event_id }
		else:
			event['dates'].add(date)
			event['times'].add(time)

	add_to_list(event_list, event)
	return event_list


def add_to_list(event_list, event):
	if bool(event):
		event['dates'] = sorted(event['dates'])
		event['times'] = sorted(event['times'])
		event_list.append(event)
'''
