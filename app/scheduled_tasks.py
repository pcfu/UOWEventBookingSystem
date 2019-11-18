from app import db
from app.models.events import Event, EventSlot
from app.models.payments import EventPromotion
from datetime import datetime, timedelta


def deactivate_expired_slots():
	active_events = Event.query.filter(Event.has_active_slots == True).all()
	error_count = 0

	for event in active_events:
		for slot in event.slots:
			# Deactivate slots that will start less than an hour from current time
			try:
				if slot.event_date <= datetime.now() + timedelta(hours = 1):
					slot.is_active = False
			except Exception as e:
				print(str(e))
				error_count += 1

			# Commit changes to db
			try:
				db.session.commit()
			except Exception as e:
				db.session.rollback()
				print(str(e))
				error_count += 1

		# Delaunch events if all active slots were deactivated
		try:
			if not event.has_active_slots:
				event.is_launched = False
		except Exception as e:
			print(str(e))
			error_count += 1

		# Commit changes to db
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			print(str(e))
			error_count += 1

	# Print job summary
	print('JOB: deactivate_expired_slots completed with {} error(s)'.format(error_count))


def deactivate_expired_event_promotions():
	eps = EventPromotion.query.filter(EventPromotion.is_active).all()
	error_count = 0

	for ep in eps:
		try:
			if ep.promotion.date_end < datetime.now().date():
				ep.is_active = False
		except Exception as e:
			print(str(e))
			error_count += 1

		# Commit changes to db
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			print(str(e))
			error_count += 1

	# Print job summary
	print('JOB: deactivate_expired_event_promotions completed with {} error(s)'.format(error_count))
