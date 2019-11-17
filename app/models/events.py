from app import db
#from app.models.booking import Booking
from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from dateutil.parser import parse
from datetime import timedelta


class Venue(db.Model):
	__tablename__ = 'venue'
	venue_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, index=True, unique=True, nullable=False)

	events = db.relationship('Event', back_populates='venue')

	def __repr__(self):
		return self.name


class EventType(db.Model):
	__tablename__ = 'event_type'
	type_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, index=True, unique=True, nullable=False)

	events = db.relationship('Event', back_populates='event_type')

	def __repr__(self):
		return self.name


class Event(db.Model):
	__tablename__ = 'event'
	event_id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String, index=True, nullable=False)
	duration = db.Column(db.Float, nullable=False)
	capacity = db.Column(db.Integer, nullable=False)
	description = db.Column(db.String)
	price = db.Column(db.Float, nullable=False)
	img_root = db.Column(db.String)
	is_launched = db.Column(db.Boolean, nullable=False)
	type_id = db.Column(db.Integer, ForeignKey('event_type.type_id'))
	venue_id = db.Column(db.Integer, ForeignKey('venue.venue_id'))

	event_type = db.relationship('EventType', back_populates='events')
	venue = db.relationship('Venue', back_populates='events')
	slots = db.relationship('EventSlot', cascade='all, delete', back_populates='event')
	#promo_pairings = db.relationship('EventPromotion', cascade='all, delete', back_populates='event')

	def __repr__(self):
		return '[ EID:{:0>4} ] {}'\
			.format(self.event_id, self.title)

	@hybrid_property
	def has_active_slots(self):
		active_slots = [slot for slot in self.slots if slot.is_active]
		return bool(active_slots)

	@has_active_slots.expression
	def has_active_slots(cls):
		return db.exists().where(db.and_(EventSlot.event_id == cls.event_id,
										 EventSlot.is_active == True))\
						  .correlate(cls)

	@hybrid_property
	def last_active_date(self):
		last_date = None
		for slot in [slot for slot in self.slots if slot.is_active]:
			if not last_date or slot.event_date.date() > last_date:
				last_date = slot.event_date.date()
		return last_date

	@last_active_date.expression
	def last_active_date(cls):
		return db.select([db.func.max(EventSlot.event_date)])\
				 .where(EventSlot.event_id == cls.event_id)\
				 .correlate(cls).as_scalar()


class EventSlot(db.Model):
	__tablename__ = 'event_slot'
	slot_id = db.Column(db.Integer, primary_key=True)
	event_date = db.Column(db.DateTime, nullable=False)
	is_active = db.Column(db.Boolean)
	event_id = db.Column(db.Integer, ForeignKey('event.event_id'))

	event = db.relationship('Event', back_populates='slots')
	#bookings = db.relationship('Booking', back_populates='slot')

	def __repr__(self):
		return "[ SID:{:0>4} ] Date: {}"\
			.format(self.slot_id, self.event_date, self.event_id)

	@hybrid_property
	def start_time(self):
		dt = parse(str(self.event_date))
		return dt.time().strftime('%I:%M %p')

	@start_time.expression
	def start_time(cls):
		return db.func.time(cls.event_date)

	@hybrid_property
	def end_time(self):
		rec = Event.query.filter(Event.event_id == self.event_id).first()
		duration = rec.duration * 60
		derived_time = self.event_date + timedelta(minutes=duration)
		dt = parse(str(derived_time))
		return dt.time().strftime('%I:%M %p')

	@end_time.expression
	def end_time(cls):
		durationSQL = Event.query.with_entities(Event.duration * 60)\
						   .filter(Event.event_id == cls.event_id).as_scalar()
		duration = '+' + durationSQL.cast(db.String) + ' minutes'
		return db.func.time(cls.event_date, duration)

	@hybrid_property
	def is_launched(self):
		return bool(self.event.is_launched)

	@is_launched.expression
	def is_launched(cls):
		return db.exists().where(db.and_(Event.event_id == cls.event_id,
										 Event.is_launched == True)).correlate(cls)

	# TEMP PROPERTY
	@property
	def vacancy(self):
		return self.event.capacity

	'''
	@hybrid_property
	def vacancy(self):
		seats = self.event.capacity
		for booking in self.bookings:
			seats -= booking.quantity
		return seats

	@vacancy.expression
	def vacancy(cls):
		occupied = db.select([db.func.ifnull(db.func.sum(Booking.quantity), 0)])\
					 .where(Booking.event_slot_id == cls.slot_id)\
					 .correlate(cls)
		return db.select([Event.capacity - occupied])\
				 .where(Event.event_id == cls.event_id)\
				 .correlate(cls)

	@hybrid_property
	def num_bookings(self):
		return len(self.bookings)

	@num_bookings.expression
	def num_bookings(cls):
		return db.select([db.func.count(Booking.booking_id)])\
				 .where(Booking.event_slot_id == cls.slot_id)\
				 .label('num_bookings')
	'''
