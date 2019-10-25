from app import app, db
from app.models import Event, EventSlot


def query_all():
	records = db.session.query(Event.event_id, Event.event_title).\
				order_by(Event.event_title).all()
	return records


def title_query(keyword):
	records = db.session.query(Event.event_id, Event.event_title).\
				filter(Event.event_title.ilike(f'%{keyword}%')).\
				order_by(Event.event_title).all()
	return records

def type_query(keyword):
	records = db.session.query(Event.event_id, Event.event_title, Event.event_type).\
				filter(Event.event_type.ilike(f'%{keyword}%')).\
				order_by(Event.event_title).all()
	return records


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
