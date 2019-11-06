from app import app, db, query
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
from sqlalchemy.sql import func
from dateutil.parser import parse
import ast, datetime


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
								   event_list=get_events(search_type, keyword),
								   add_admin_btn=(is_staff_user() or is_admin_user()))

	return render_template('index.html', title='Event Booking System',
						   form=form, event_list=get_events(),
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
		return redirect(url_for('admin.index'))

	# renders staff login page
	return render_template('staff_login.html', title='EBS: Admin', form=form)


@app.route('/logout')
def logout():
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


@app.route('/event/details/<eid>')
def event_details(eid):
	records = query.details_query(eid)
	if not records:
		return redirect(url_for('index'))
	else:
		event = query.format_records(records)

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
		uid = current_user.user_id
		esid = form.times.data
		qty = form.count.data
		return redirect((url_for('payment', booking_details={
												'event_id': eid,
												'user_id': uid,
												'slot_id': esid,
												'quantity': qty,
												'price': event.price })
						))

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


@app.route('/booking/payment/<booking_details>', methods=['GET', 'POST'])
def payment(booking_details):
	if not current_user.is_authenticated:
		return redirect(url_for('user_login'))
	elif is_admin_user():
		return redirect(url_for('event_details', eid=booking_details['event_id']))

	form = PaymentForm()
	# typecast booking_details to dict. redirect converts it to a dict str literal
	booking_details = ast.literal_eval(booking_details)
	booking_details['title'] = Event.query.get(booking_details['event_id']).title
	booking_details['time'] = EventSlot.query.get(booking_details['slot_id']).event_date

	if form.validate_on_submit():
		booking = Booking(user_id=booking_details['user_id'],
						event_slot_id=booking_details['slot_id'],
						quantity=booking_details['quantity'])
		db.session.add(booking)
		db.session.commit()

		amount = booking_details['price'] * booking_details['quantity']
		payment = Payment(booking_id=booking.booking_id, amount=amount,
						  card_number=form.card_number.data)
		db.session.add(payment)
		db.session.commit()
		return render_template('confirm_booking.html')

	return render_template('payment.html', form=form, booking_details=booking_details,
	 						add_admin_btn=(is_staff_user() or is_admin_user()))


########################
# SUPPORTING FUNCTIONS #
########################

def get_events(search_type=None, keyword=None):
	if keyword is None:
		return query.query_all()
	elif search_type == 'title':
		return query.title_query(keyword)
	elif search_type == 'type':
		return query.type_query(keyword)
	elif search_type == 'date':
		return query.date_query(keyword)
	else:
		return query.price_query(keyword)
