from app import db
from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property


class Payment(db.Model):
	__tablename__ = 'payment'
	payment_id = db.Column(db.Integer, primary_key=True)
	quantity = db.Column(db.Integer, nullable=False)
	amount = db.Column(db.Float, nullable=False)
	card_number = db.Column(db.Integer, nullable=False)
	booking_id = db.Column(db.Integer, ForeignKey('booking.booking_id'), nullable=False)
	promotion_id = db.Column(db.Integer, ForeignKey('promotion.promotion_id'))

	booking = db.relationship('Booking', back_populates='payments')
	promotion = db.relationship('Promotion', back_populates='payments')
	#refunds = db.relationship('Refund', back_populates='payment')

	def __repr__(self):
		return '[ PAYID:{:0>4} ] ----- [ BID:{:0>4} ]'.format(self.payment_id, self.booking_id)

	'''
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
	'''


class Promotion(db.Model):
	__tablename__ = 'promotion'
	promotion_id = db.Column(db.Integer, primary_key=True)
	promo_percentage = db.Column(db.Integer, nullable=False)
	date_start = db.Column(db.Date, nullable=False)
	date_end = db.Column(db.Date, nullable=False)
	promo_code = db.Column(db.String, nullable=False)

	payments = db.relationship('Payment', back_populates='promotion')
	#event_pairings = db.relationship('EventPromotion', cascade='all, delete', back_populates='promotion')

	def __repr__(self):
		return '[ PROID:{:0>4} ] {}'.format(self.promotion_id, self.promo_code)

	'''
	@hybrid_property
	def has_active_event_promo(self):
		active_pairs = 0
		for ep in self.event_pairings:
			if ep.is_active:
				active_pairs += 1
		return active_pairs > 0

	@has_active_event_promo.expression
	def has_active_event_promo(cls):
		return db.select([
					db.case([(db.func.count(EventPromotion.promotion_id) > 0, True)],
							else_=False)
				]).where(db.and_(EventPromotion.is_active == True,
								 EventPromotion.promotion_id == cls.promotion_id))\
				 .correlate(cls).as_scalar()

	@hybrid_property
	def is_used(self):
		return len(self.payments) > 0

	@is_used.expression
	def is_used(cls):
		return db.select([
					db.case([(db.func.count(Payment.promotion_id) > 0, True)],
							else_=False)
				]).where(Payment.promotion_id == cls.promotion_id)\
				 .correlate(cls).as_scalar()
	'''


'''
class EventPromotion(db.Model):
	event_id = db.Column(db.Integer, ForeignKey('event.event_id'), primary_key=True)
	promotion_id = db.Column(db.Integer, ForeignKey('promotion.promotion_id'), primary_key=True)
	is_active = db.Column(db.Boolean)

	event = db.relationship('Event', back_populates='promo_pairings')
	promotion = db.relationship('Promotion', back_populates='event_pairings')

	def __repr__(self):
		return '[ EID:{:0>4} ] {} ----- [ PROID:{:0>4} ] {}'\
			.format(self.event_id, self.event.title,
					self.promotion_id, self.promotion.promo_code)


class Refund(db.Model):
	refund_id = db.Column(db.Integer, primary_key=True)
	quantity = db.Column(db.Integer, nullable=False)
	payment_id = db.Column(db.Integer, ForeignKey('payment.payment_id'))

	payment = db.relationship('Payment', back_populates='refunds')

	def __repr__(self):
		return '[ RID:{} ] ----- Quantity: {}'.format(self.refund_id, self.quantity)

	@hybrid_property
	def refund_amount(self):
		return self.payment.amount / self.payment.quantity * self.quantity

	@refund_amount.expression
	def refund_amount(cls):
		return db.select([Payment.amount / Payment.quantity * cls.quantity])\
				 .where(Payment.payment_id == cls.payment_id).correlate(cls).as_scalar()
'''
