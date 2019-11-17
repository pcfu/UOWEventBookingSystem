from app import db
from sqlalchemy import ForeignKey


class Booking(db.Model):
	__tablename__ = 'booking'
	booking_id = db.Column(db.Integer, primary_key=True)
	quantity = db.Column(db.Integer, nullable=False)
	user_id = db.Column(db.Integer, ForeignKey('user.user_id'))
	event_slot_id = db.Column(db.Integer, ForeignKey('event_slot.slot_id'))

	user = db.relationship('User', back_populates='bookings')
	slot = db.relationship('EventSlot', back_populates='bookings')
	#payments = db.relationship('Payment', back_populates='booking')

	def __repr__(self):
		return "Booking No: {}\nUserID: {}".format(self.booking_id, self.user_id)
