from app import db
from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property


class Payment(db.Model):
	payment_id = db.Column(db.Integer, primary_key=True)
	quantity = db.Column(db.Integer, nullable=False)
	amount = db.Column(db.Float, nullable=False)
	card_number = db.Column(db.Integer, nullable=False)
	booking_id = db.Column(db.Integer, ForeignKey('booking.booking_id'), nullable=False)
	promotion_id = db.Column(db.Integer, ForeignKey('promotion.promotion_id'))

	booking = db.relationship('Booking', back_populates='payments')
	promotion = db.relationship('Promotion', back_populates='payments')
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

	@hybrid_property
	def is_cancelled(self):
		return self.quantity == self.total_refund_qty


class Promotion(db.Model):
	promotion_id = db.Column(db.Integer, primary_key=True)
	promo_percentage = db.Column(db.Integer)
	dt_start = db.Column(db.DateTime)
	dt_end = db.Column(db.DateTime)
	promo_code = db.Column(db.String)

	payments = db.relationship('Payment', back_populates='promotion')
	event_pairings = db.relationship('EventPromotion', back_populates='promotion')

	def __repr__(self):
		return '[ PROID:{:0>4} ] {}'.format(self.promotion_id, self.promo_code)


class EventPromotion(db.Model):
	event_id = db.Column(db.Integer, ForeignKey('event.event_id'), primary_key=True)
	promotion_id = db.Column(db.Integer, ForeignKey('promotion.promotion_id'), primary_key=True)
	is_active = db.Column(db.Boolean)

	event = db.relationship('Event', back_populates='promo_pairings')
	promotion = db.relationship('Promotion', back_populates='event_pairings')


class Refund(db.Model):
	refund_id = db.Column(db.Integer, primary_key=True)
	quantity = db.Column(db.Integer, nullable=False)
	payment_id = db.Column(db.Integer, ForeignKey('payment.payment_id'))

	payment = db.relationship('Payment', back_populates='refunds')

	def __repr__(self):
		return '[ RID:{} ] ----- Quantity: {}'.format(self.refund_id, self.quantity)
