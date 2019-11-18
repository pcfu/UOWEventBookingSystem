from app import db
from app.models.events import EventType, Event, EventSlot
from app.models.booking import Booking
from app.models.payments import Payment
from app.models.logs import LoginHistory, LogoutHistory
from flask_login import current_user
from sqlalchemy.sql import func
from dateutil.parser import parse
from datetime import datetime


def add_login_record():
	log = LoginHistory(timestamp=datetime.now(), user_id=current_user.user_id)
	db.session.add(log)
	db.session.commit()


def add_logout_record():
	log = LogoutHistory(timestamp=datetime.now(), user_id=current_user.user_id)
	db.session.add(log)
	db.session.commit()


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


def details_query(eid):
	return db.session.query(Event, EventSlot)\
					 .join(EventSlot, Event.event_id == EventSlot.event_id)\
					 .filter(Event.event_id == eid,
							 Event.is_launched,
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


def format_events(records):
	event = { 'title' : records[0].Event.title,
			  'venue' : records[0].Event.venue,
			  'timings' : dict(),
			  'duration' : int(records[0].Event.duration * 60),
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
						  'vacancy' : row.slot.vacancy,
						  'qty' : row.quantity,
						  'is_active' : row.slot.event.is_launched and
						  				row.slot.is_active
						})
	return bookings


def update_booking_payment(form, payment):
	# Update db with new booking or edit existing booking
	if payment['booking_type'] == 'new':
		booking = Booking(user_id=payment['user_id'],
						  event_slot_id=payment['slot_id'],
						  quantity=payment['quantity'])
		db.session.add(booking)
	elif payment['booking_type'] == 'update':
		booking = Booking.query.get(payment['booking_id'])
		booking.quantity += payment['quantity']
	db.session.commit()

	# Update db with new payment record
	new_payment = Payment(quantity=payment['quantity'],
						  amount=(payment['price'] * payment['quantity']),
						  card_number=form.card_number.data,
						  booking_id=booking.booking_id,
						  promotion_id=payment['promo_id'])
	db.session.add(new_payment)
	db.session.commit()


########################
# Supporting Functions #
########################

def query_all():
	return db.session.query(Event.event_id, Event.title, Event.img_root)\
					 .filter(Event.is_launched)\
					 .order_by(Event.title).all()

	'''
	return db.session.query(Event.event_id, Event.title, Event.img_root)\
					 .filter(Event.is_launched, Event.has_active_slots)\
					 .join(EventSlot, Event.event_id == EventSlot.event_id)\
					 .group_by(Event.event_id).order_by(Event.title).all()
	'''


def title_query(keyword):
	return db.session.query(Event.event_id, Event.title, Event.img_root)\
					 .filter(Event.is_launched, Event.title.ilike(f'%{keyword}%'))\
					 .order_by(Event.title).all()

	'''
	return db.session.query(Event.event_id, Event.title, Event.img_root)\
					 .filter(Event.is_launched, Event.has_active_slots,
							 Event.title.ilike(f'%{keyword}%'))\
					 .join(EventSlot, Event.event_id == EventSlot.event_id)\
					 .group_by(Event.event_id).order_by(Event.title).all()
	'''


def type_query(keyword):
	return db.session.query(Event.event_id, Event.title, Event.img_root)\
					 .join(EventType, Event.type_id == EventType.type_id)\
					 .filter(Event.is_launched, EventType.name == keyword)\
					 .order_by(Event.title).all()

	'''
	return db.session.query(Event.event_id, Event.title, Event.img_root)\
					 .join(EventType, Event.type_id == EventType.type_id)\
					 .filter(Event.is_launched, Event.has_active_slots,
							 EventType.name == keyword)\
					 .join(EventSlot, Event.event_id == EventSlot.event_id)\
					 .group_by(Event.event_id).order_by(Event.title).all()
	'''


def date_query(keyword):
	return db.session.query(Event.event_id, Event.title, Event.img_root)\
					 .join(EventSlot, Event.event_id == EventSlot.event_id)\
					 .filter(func.DATE(EventSlot.event_date) >= keyword['from_date'],
							 func.DATE(EventSlot.event_date) <= keyword['to_date'])\
					 .group_by(Event.event_id).order_by(Event.title).all()


def price_query(keyword):
	'''
	records = db.session.query(Event.event_id, Event.title,
							   Event.price, Event.img_root)\
						.filter(Event.is_launched, Event.has_active_slots)\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.group_by(Event.event_id).order_by(Event.title)
	'''

	records = db.session.query(Event.event_id, Event.title,
							   Event.price, Event.img_root)\
						.filter(Event.is_launched)\
						.order_by(Event.title)

	if keyword == 'free':
		records = records.filter(Event.price == 0).all()
	elif keyword == 'cheap':
		records = records.filter(Event.price < 20).all()
	elif keyword == 'mid':
		records = records.filter(Event.price >= 20, Event.price <= 50 ).all()
	else:
		records = records.filter(Event.price > 50).all()

	return records
