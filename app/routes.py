from dateutil.parser import parse
from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import MemberLoginForm, AdminLoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Staff, Event, EventSlot

# url_for will ALWAYS be function name

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title='Events Booking System')


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
		return redirect(url_for('index'))

	# render login page
	return render_template('login.html', title='Sign In', form=form)


@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
	# if already logged in redirect to homepage
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = AdminLoginForm()
	if form.validate_on_submit():
		staff = Staff.query.filter_by(username=form.username.data).first()
		login_user(staff, remember=form.remember_me.data)
		#redirect to admin page using flask_admin(endpoint=admin)
		return redirect(url_for('admin.index'))

	# renders staff login page
	return render_template('staff_login.html', title='Admin Sign In', form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	# if already logged in redirect to homepage
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		login_user(user)
		return redirect(url_for('index'))
	return render_template('register.html', page_title='Account Registration', form=form)


@app.route('/event')
def show_events():
	return render_template('event.html', title='Events', event_list=get_all_events())


### Functions to support Event queries and display format
def get_all_events():
	event_list = []

	events = db.session.query(Event).all()
	for event in events:
		date_first = [None]
		date_last = [None]
		timeslots = set()
		load_date_time(date_first, date_last, timeslots, event.event_id)
		dates_str = get_pretty_date(date_first[0], date_last[0])
		times_str = get_pretty_time(timeslots)

		event_list.append({ 'title' : event.event_title,
							'venue' : event.venue,
							'date' : dates_str,
							'time' : times_str,
							'duration' : event.duration,
							'capacity' : event.capacity,
							'type': event.event_type,
							'desc': event.description,
							'price' : event.price,
							'event_id' : event.event_id })
	return event_list


def load_date_time(date_first, date_last, timeslots, eid):
	for slot in db.session.query(EventSlot).filter_by(event_id = eid).\
					order_by(EventSlot.event_date).all():
		dt = parse(str(slot.event_date))
		date = dt.date()
		if date_first[0] is None:
			date_first[0] = date
		date_last[0] = date

		time = dt.time().strftime('%H:%M')
		timeslots.add(time)


def get_pretty_date(date_first, date_last):
	period = str(date_first)
	if date_last != date_first:
		period += " to " + str(date_last)
	return period


def get_pretty_time(timeslots):
	schedule = ""
	for time in sorted(timeslots):
		if schedule:
			schedule += ", "
		schedule += str(time)
	return schedule
