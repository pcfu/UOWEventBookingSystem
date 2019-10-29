from app import db
from sqlalchemy import ForeignKey
from dateutil.parser import parse
from datetime import timedelta


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
	type_id = db.Column(db.Integer, ForeignKey('event_type.type_id'))
	venue_id = db.Column(db.Integer, ForeignKey('venue.venue_id'))

	event_type = db.relationship('EventType', back_populates='events')
	venue = db.relationship('Venue', back_populates='events')
	slots = db.relationship('EventSlot', cascade='all, delete', back_populates='event')

	def __repr__(self):
		return '[ EID:{} ] {} ---------- [ {} ]'\
			.format(self.event_id, self.title, self.venue)

	@property
	def is_scheduled(self):
		return bool(self.slots)


class EventSlot(db.Model):
	slot_id = db.Column(db.Integer, primary_key=True)
	event_date = db.Column(db.DateTime, nullable=False)
	event_id = db.Column(db.Integer, ForeignKey('event.event_id'))

	event = db.relationship('Event', back_populates='slots')
	#bookings = db.relationship('Booking', back_populates='slot')

	def __repr__(self):
		return "[ EID:{} ] {} ------ Date: {}"\
			.format(self.event_id, self.event.title, self.event_date)

	@property
	def start_time(self):
		dt = parse(str(self.event_date))
		return dt.time().strftime('%I:%M %p')

	@property
	def end_time(self):
		rec = Event.query.filter(Event.event_id == self.event_id).first()
		duration = rec.duration * 60
		derived_time = self.event_date + timedelta(minutes=duration)
		dt = parse(str(derived_time))
		return dt.time().strftime('%I:%M %p')