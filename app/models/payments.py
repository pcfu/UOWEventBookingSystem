from app import db
from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property


class Payment(db.Model):
	payment_id = db.Column(db.Integer, primary_key=True)
	quantity = db.Column(db.Integer, nullable=False)
	amount = db.Column(db.Integer, nullable=False)
	card_number = db.Column(db.Integer, nullable=False)
	booking_id = db.Column(db.Integer, ForeignKey('booking.booking_id'), nullable=False)

	booking = db.relationship('Booking', back_populates='payments')
	refunds = db.relationship('Refund', back_populates='payment')

	def __repr__(self):
		return 'Payment No: {}\nBooking ID: {}'\
			.format(self.payment_id, self.booking_id)

	@hybrid_property
	def total_refund_qty(self):
		total = 0
		for refund in self.refunds:
			total += refund.quantity
		return total

	@total_refund_qty.expression
	def total_refund_qty(cls):
		return db.select([db.func.ifnull(db.func.sum(Refund.quantity), 0)])\
				 .where(Refund.payment_id == cls.payment_id)\
				 .correlate(cls)


class Refund(db.Model):
	refund_id = db.Column(db.Integer, primary_key=True)
	quantity = db.Column(db.Integer, nullable=False)
	payment_id = db.Column(db.Integer, ForeignKey('payment.payment_id'))

	payment = db.relationship('Payment', back_populates='refunds')

	def __repr__(self):
		return '[ RID:{} ] ----- Quantity: {}'.format(self.refund_id, self.quantity)
