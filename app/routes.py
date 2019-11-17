from app import app, db, db_tools
from app.models.users import User
from app.models.events import EventType, Event #, EventSlot
#from app.models.booking import Booking
#from app.models.payments import Payment, EventPromotion, Promotion, Refund
from app.forms.forms import LoginForm, RegistrationForm, SearchForm
#							BookingForm, PaymentForm, AccountUpdateForm
from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import current_user, login_user, logout_user
#from app.views.utils import is_admin_user, is_staff_user
from flask import flash


@app.login_manager.user_loader
def load_user(id_):
	return User.query.get(int(id_))


@app.route('/')
@app.route('/index')
@app.route('/search')
def index():
	return redirect(url_for('get_events', option='title'))


@app.route('/search/<option>', methods=['GET', 'POST'])
def get_events(option):
	form = SearchForm()
	form.search_type.data = option
	if option == 'date':
		form.search_field = form.DATE_FIELD
	elif option == 'price':
		form.search_field = form.PRICE_FIELD
	elif option == 'type':
		form.search_field = form.TYPE_FIELD

	#if form.is_submitted():
	if form.validate_on_submit():
		search_type = form.search_type.data
		if not option == 'date':
			keyword = str(form.search_field.data).strip()
		else:
			keyword = form.search_field.data

		if len(keyword) > 0:
			return render_template(
				'index.html', title='Event Booking System', form=form,
				event_list=db_tools.get_event_list(search_type, keyword))

	return render_template('index.html', title='Event Booking System',
						   form=form, event_list=db_tools.get_event_list())


@app.route('/event/details/<eid>')
def event_details(eid):
	# Redirect to homepage if no event with specified eid
	records = db_tools.details_query(eid)
	if not records:
		return redirect(url_for('index'))

	event = db_tools.format_events(records)
	return render_template('details.html',
						   title='EBS: {}'.format(event['title']),
						   event=event)


@app.route('/login', methods=['GET', 'POST'])
def login():
	# if already logged in redirect to homepage
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		login_user(user, remember=form.remember_me.data)
		db_tools.add_login_record()
		session['payment_due'] = None

		# return regular users to homepage; staff users to admin page
		if user.is_regular():
			return redirect(url_for('index'))
		else:
			return redirect(url_for('admin.index'))

	# render login page
	return render_template('login.html', title='EBS: Sign In', form=form)


@app.route('/logout')
def logout():
	session['payment_due'] = None
	db_tools.add_logout_record()
	logout_user()
	return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	# if already logged in redirect to homepage
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = RegistrationForm()
	if form.validate_on_submit():
		# Add new user record to db
		new_user = User(username=form.username.data, email=form.email.data, group_id=1)
		new_user.set_password(form.password.data)
		db.session.add(new_user)
		db.session.commit()

		# Autologin and redirect new user
		login_user(new_user)
		db_tools.add_login_record()
		session['payment_due'] = None
		return redirect(url_for('index'))

	return render_template('register.html', title='EBS: Account Registration', form=form)


@app.route('/my_account', methods=['GET', 'POST'])
def my_account():
	return 'My account page'

	'''
	# Redirect to other endpoint if pre-reqs not met
	if not current_user.is_authenticated:
		return redirect(url_for('index'))

	update_form = AccountUpdateForm()
	# Update email if validation checks passed
	if 'update_email-update_email' in request.form \
		and update_form.update_email.validate_on_submit():
			current_user.email = update_form.update_email.email.data
			db.session.commit()
			flash('Email updated successfully')
	# Update password if validation checks passed
	elif 'update_password-update_password' in request.form \
		 and update_form.update_password.validate_on_submit():
			current_user.set_password(update_form.update_password.new_password.data)
			db.session.commit()
			flash('Password updated successfully')

	# Reset form fields
	update_form.update_email.email.data = None
	update_form.update_password.old_password.data = None
	update_form.update_password.new_password.data = None
	update_form.update_password.confirm_password.data = None
	return render_template('my_account.html', update_form=update_form,
						   is_admin=is_admin_user(), is_staff=is_staff_user())
	'''

@app.route('/my_bookings')
def my_bookings():
	return 'My bookings page'
	'''
	# Redirect to other endpoint if pre-reqs not met
	if not current_user.is_authenticated:
		return redirect(url_for('user_login'))
	elif is_admin_user():
		return redirect(url_for('index'))

	records = Booking.query.filter(Booking.user_id == current_user.user_id,
								   Booking.quantity > 0).all()
	bookings = query.format_bookings(records)
	return render_template('my_bookings.html', bookings=bookings,
						   is_admin=is_admin_user(), is_staff=is_staff_user())


@app.route('/my_bookings/add_to/<bid>/<delta>')
def add_to_booking(bid, delta):
	# Redirect to other endpoint if pre-reqs not met
	booking = Booking.query.get(bid)
	if not current_user.is_authenticated:
		return redirect(url_for('user_login'))
	elif is_admin_user() or current_user.user_id != booking.user_id:
		return redirect(url_for('index'))

	# Save payment details in current session object
	session['payment_due'] = {'event_id' : booking.slot.event.event_id,
							  'user_id' : current_user.user_id,
							  'slot_id' : booking.event_slot_id,
							  'quantity' : int(delta),
							  'price' : booking.slot.event.price,
							  'booking_type' : 'update',
							  'booking_id' : bid}
	return redirect(url_for('payment'))


@app.route('/my_bookings/cancel/<bid>/<delta>')
def cancel_booking(bid, delta):
	# Redirect to other endpoint if pre-reqs not met
	booking = Booking.query.get(bid)
	if not current_user.is_authenticated:
		return redirect(url_for('user_login'))
	elif is_admin_user() or current_user.user_id != booking.user_id:
		return redirect(url_for('index'))

	# Throw error if requested refund quantity exceeds total booking quantity
	request_balance = int(delta)
	if request_balance > booking.quantity:
		return render_template('error.html', e_msg='Error in refund quantity.',
							   page='your bookings page',
							   redirect_url=url_for('my_bookings'),
							   is_admin=is_admin_user(), is_staff=is_staff_user())

	# Loop through payments to refund as much request_balance as possible
	refund_amount = 0.0
	for payment in booking.payments:
		if request_balance > 0:
			payment_avail_refunds = payment.quantity - payment.total_refund_qty
			if payment_avail_refunds > 0:
				# Add new refund record to db
				new_refund_qty = min(payment_avail_refunds, request_balance)
				new_refund = Refund(quantity=new_refund_qty,
									payment_id=payment.payment_id)
				db.session.add(new_refund)

				# Update cumulative changes
				booking.quantity -= new_refund_qty
				refund_amount += payment.amount / payment.quantity * new_refund_qty
				request_balance -= new_refund_qty

	# Rollback db and throw error if created refunds exceed total booking quantity
	if request_balance < 0:
		db.session.rollback()
		return render_template('error.html', e_msg='Refund processing error.',
							   page='your bookings page',
							   redirect_url=url_for('my_bookings'),
							   is_admin=is_admin_user(), is_staff=is_staff_user())

	# Commit changes and redirect to confirmation page
	db.session.commit()
	details = query.format_bookings([booking])[0]
	return render_template('confirm_refund.html',
						   amount=refund_amount, qty=delta, details=details,
						   is_admin=is_admin_user(), is_staff=is_staff_user())
'''


@app.route('/booking/<eid>', methods=['GET', 'POST'])
def booking(eid):
	# Redirect to other endpoint if pre-reqs not met
	if not current_user.is_authenticated:
		return redirect(url_for('login'))
	elif current_user.is_admin():
		return redirect(url_for('event_details', eid=eid))
	event = Event.query.get(eid)
	if not event or not event.is_launched:
		return redirect(url_for('index'))

	return 'Book event {}'.format(eid)

	'''
	# Create booking form
	form = BookingForm()
	form.preload(current_user, event)
	if form.is_submitted():
		# Load payment details into session
		session['payment_due'] = {'event_id' : eid,
								  'user_id' : current_user.user_id,
								  'slot_id' : form.time.data,
								  'quantity' : form.count.data,
								  'price' : round(event.price,2),
								  'booking_type' : 'new'}
		return redirect(url_for('payment'))

	return render_template('booking.html', form=form, eid=eid,
						   is_admin=is_admin_user(), is_staff=is_staff_user())
	'''

'''
@app.route('/booking/<eid>/<date>')
def booking_slot(eid, date):
	timings = []

	records = query.event_times_query(eid, date)
	for rec in records:
		# Only add timings for slots that still have available seats
		if rec.vacancy > 0:
			timing = {}
			timing['slot_id'] = rec.slot_id
			timing['time'] = rec.time
			timing['vacancy'] = EventSlot.query.get(rec.slot_id).vacancy
			timings.append(timing)

	return jsonify({ 'timings' : timings })


@app.route('/booking/vacancy/<sid>')
def booking_vacancy(sid):
	vacancy = EventSlot.query.get(sid).vacancy
	return jsonify({ 'vacancy' : vacancy })


@app.route('/booking/payment', methods=['GET', 'POST'])
def payment():
	# Redirect to other endpoint if pre-reqs not met
	if not current_user.is_authenticated:
		return redirect(url_for('user_login'))
	elif is_admin_user() or session['payment_due'] is None:
		return redirect(url_for('index'))

	# Retrieve payment details from session object
	payment = session['payment_due']
	payment['title'] = Event.query.get(payment['event_id']).title
	payment['time'] = EventSlot.query.get(payment['slot_id']).event_date
	if not 'promo_id' in payment:
		payment['promo_id'] = None

	form = PaymentForm()
	form.promo.promo_event_id.data = payment['event_id']

	# Promotion code applied
	if 'promo-apply_promo' in request.form and form.promo.validate_on_submit():
		promo_record = Promotion.query.filter(Promotion.promo_code ==
											  form.promo.promo_code.data).first()
		base_price = Event.query.get(payment['event_id']).price
		discount = promo_record.promo_percentage
		payment['price'] =  base_price * (1-discount/100)
		payment['promo_id'] = promo_record.promotion_id
		form.promo.current_code_applied.data = form.promo.promo_code.data
		form.promo.promo_code.data = None
	# Payment submitted
	elif 'submit' in request.form and form.validate_on_submit():
		# Throw error if booking quantity more than current slot vacancy
		current_vacancy = EventSlot.query.get(payment['slot_id']).vacancy
		if payment['quantity'] > current_vacancy:
			session['[payment_due'] = None
			return render_template(
				'error.html',
				e_msg='{}{}'.format('Number of tickets exceed available seats. ',
									'Please edit your booking.'),
				page='booking page',
				redirect_url=url_for('booking', eid=payment['event_id']),
				is_admin=is_admin_user(), is_staff=is_staff_user())

		# Update db
		db_update_booking_payment(form=form, payment=payment)

		# Clear session object and confirm booking
		session['payment_due'] = None
		is_new_booking = payment['booking_type'] == 'new'
		return render_template('confirm_booking.html',
							   redirect_homepage=is_new_booking,
							   is_admin=is_admin_user(),
							   is_staff=is_staff_user())

	return render_template('payment.html', form=form, booking_details=payment,
						   is_admin=is_admin_user(), is_staff=is_staff_user())


#####################################
# Supporting function for payment() #
#####################################

def db_update_booking_payment(form, payment):
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
'''
