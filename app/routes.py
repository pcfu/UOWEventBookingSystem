from app import app, db, query, session
from app.models.payments import Payment
from app.models.users import User, Admin
from app.models.events import Event, EventSlot
from app.models.booking import Booking
from app.models.logs import add_login_record, add_logout_record
from app.forms.forms import MemberLoginForm, StaffLoginForm, RegistrationForm, \
							SearchForm, BookingForm, PaymentForm
from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import current_user, login_user, logout_user
from app.views.utils import is_admin_user, is_staff_user
import ast


@app.login_manager.user_loader
def load_user(entry):
	if entry[0] == 'User':
		return User.query.get(int(entry[1]))
	else:
		return Admin.query.get(int(entry[1]))


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

	if form.is_submitted():
		search_type = form.search_type.data
		keyword = str(form.search_field.data).strip()
		if len(keyword) > 0:
			return render_template('index.html', title='Event Booking System', form=form,
								   event_list=query.get_event_list(search_type, keyword),
								   add_admin_btn=(is_staff_user() or is_admin_user()))

	return render_template('index.html', title='Event Booking System',
						   form=form, event_list=query.get_event_list(),
						   add_admin_btn=(is_staff_user() or is_admin_user()))



@app.route('/login', methods=['GET', 'POST'])
def user_login():
	# if already logged in redirect to homepage
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = MemberLoginForm()
	if form.validate_on_submit():
		# if login is successful, return user to 'index'
		user = User.query.filter_by(username=form.username.data).first()
		login_user(user, remember=form.remember_me.data)
		add_login_record()
		session['payment_due'] = None
		return redirect(url_for('index'))

	# render login page
	return render_template('login.html', title='EBS: Sign In', form=form)


@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
	# if already logged in redirect to admin page
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = StaffLoginForm()
	if form.validate_on_submit():
		staff = query.staff_user_query(form.username.data)
		login_user(staff, remember=form.remember_me.data)
		add_login_record()
		session['payment_due'] = None
		return redirect(url_for('admin.index'))

	# renders staff login page
	return render_template('staff_login.html', title='EBS: Admin', form=form)


@app.route('/logout')
def logout():
	session['payment_due'] = None
	add_logout_record()
	logout_user()
	return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	# if already logged in redirect to homepage
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = RegistrationForm()
	if form.validate_on_submit():
		new_user = User(username=form.username.data,
						email=form.email.data,
						is_staff=False)
		new_user.set_password(form.password.data)
		db.session.add(new_user)
		db.session.commit()
		login_user(new_user)
		return redirect(url_for('index'))

	return render_template('register.html', title='EBS: Account Registration', form=form)


@app.route('/my_bookings')
def my_bookings():
	if not current_user.is_authenticated:
		return redirect(url_for('user_login'))
	elif is_admin_user():
		return redirect(url_for('index'))

	records = Booking.query.filter(Booking.user_id == current_user.user_id).all()
	bookings = query.format_bookings(records)
	return render_template('my_bookings.html', bookings=bookings)


## Placeholder link for edit bookings page
@app.route('/test/<bid>')
def test(bid=None):
	if bid is None:
		return redirect(url_for('index'))
	else:
		return 'Edit page for booking id ' + bid


@app.route('/event/details/<eid>')
def event_details(eid):
	records = query.details_query(eid)
	if not records:
		return redirect(url_for('index'))
	else:
		event = query.format_events(records)

	return render_template('details.html', title='EBS: ' + event['title'],
						   event=event, is_admin=is_admin_user(),
						   add_admin_btn=(is_staff_user() or is_admin_user()))


@app.route('/booking/<eid>', methods=['GET', 'POST'])
def booking(eid):
	# Redirect to other endpoint if pre-reqs not met
	if not current_user.is_authenticated:
		return redirect(url_for('user_login'))
	elif is_admin_user():
		return redirect(url_for('event_details', eid=eid))
	event = Event.query.get(eid)
	if not event or not event.is_launched or not event.has_active_slots:
		return redirect(url_for('index'))

	# Create booking form
	form = BookingForm()
	form.preload(current_user, event)
	if form.is_submitted():
		# Load payment details into session
		session['payment_due'] = {'event_id': eid,
								  'user_id': current_user.user_id,
								  'slot_id': form.times.data,
								  'quantity': form.count.data,
								  'price': event.price}
		return redirect(url_for('payment'))

	return render_template('booking.html', form=form, eid=eid,
						   add_admin_btn=(is_staff_user() or is_admin_user()))


@app.route('/booking/<eid>/<date>')
def booking_slot(eid, date):
	timings = []

	records = query.event_times_query(eid, date)
	for rec in records:
		timing = {}
		timing['slot_id'] = rec.slot_id
		timing['time'] = rec.time
		timings.append(timing)

	return jsonify({ 'timings' : timings })


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

	form = PaymentForm()
	if form.validate_on_submit():
		# Update db with new booking record
		booking = Booking(user_id=payment['user_id'],
						  event_slot_id=payment['slot_id'],
						  quantity=payment['quantity'])
		db.session.add(booking)
		db.session.commit()

		# Update db with new payment record
		payment = Payment(booking_id=booking.booking_id,
						  amount=(payment['price'] * payment['quantity']),
						  card_number=form.card_number.data)
		db.session.add(payment)
		db.session.commit()

		session['payment_due'] = None
		return render_template('confirm_booking.html')

	return render_template('payment.html', form=form, booking_details=payment,
	 						add_admin_btn=(is_staff_user() or is_admin_user()))
