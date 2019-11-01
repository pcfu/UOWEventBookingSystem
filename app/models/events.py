from app import db
from app.models.booking import Booking
from sqlalchemy import ForeignKey
from dateutil.parser import parse
from datetime import timedelta
from sqlalchemy.ext.hybrid import hybrid_property


class Venue(db.Model):
	venue_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, index=True, unique=True, nullable=False)

	events = db.relationship('Event', back_populates='venue')

	def __repr__(self):
		return self.name


class EventType(db.Model):
	type_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, index=True, unique=True, nullable=False)

	events = db.relationship('Event', back_populates='event_type')

	def __repr__(self):
		return self.name


class Event(db.Model):
	event_id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String, index=True, nullable=False)
	duration = db.Column(db.Float, nullable=False)
	capacity = db.Column(db.Integer, nullable=False)
	description = db.Column(db.String)
	price = db.Column(db.Float, nullable=False)
	img_root = db.Column(db.String)
	is_launched = db.Column(db.Boolean, nullable=False)
	type_id = db.Column(db.Integer, ForeignKey('event_type.type_id'))
	venue_id = db.Column(db.Integer, ForeignKey('venue.venue_id'), nullable=False)

	event_type = db.relationship('EventType', back_populates='events')
	venue = db.relationship('Venue', back_populates='events')
	slots = db.relationship('EventSlot', cascade='all, delete', back_populates='event')

	def __repr__(self):
		return '[ EID:{} ] {} ---------- [ {} ]'\
			.format(self.event_id, self.title, self.venue)

	@hybrid_property
	def is_scheduled(self):
		return bool(self.slots)

	@property
	def has_active_slots(self):
		active_slots = [slot for slot in self.slots if slot.is_active]
		return bool(active_slots)


class EventSlot(db.Model):
	slot_id = db.Column(db.Integer, primary_key=True)
	event_date = db.Column(db.DateTime, nullable=False)
	is_active = db.Column(db.Boolean)
	event_id = db.Column(db.Integer, ForeignKey('event.event_id'))

	event = db.relationship('Event', back_populates='slots')
	bookings = db.relationship('Booking', back_populates='slot')

	def __repr__(self):
		return "[ EID:{} ] {} ------ Date: {}"\
			.format(self.event_id, self.event.title, self.event_date)

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
		return db.select([
					db.case([( db.exists()\
							   .where(db.and_(Event.event_id == cls.event_id,
											  Event.is_launched == True))\
							   .correlate(cls), True)],
							else_=False)
				])

	@hybrid_property
	def num_bookings(self):
		return len(self.bookings)

	@num_bookings.expression
	def num_bookings(cls):
		return db.select([db.func.count(Booking.booking_no)])\
				 .where(Booking.event_slot_id == cls.slot_id)\
				 .label('num_bookings')
