from app import db
from sqlalchemy import ForeignKey

class Payment(db.Model):
	payment_id = db.Column(db.Integer, primary_key=True)
	quantity = db.Column(db.Integer, nullable=False)
	amount = db.Column(db.Integer, nullable=False)
	card_number = db.Column(db.Integer, nullable=False)
	booking_id = db.Column(db.Integer, ForeignKey('booking.booking_id'), nullable=False)

	booking = db.relationship('Booking', back_populates='payments')

	def __repr__(self):
		return "Payment No: {}\nBooking ID: {}"\
			.format(self.payment_id, self.booking_id)
