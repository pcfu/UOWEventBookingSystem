from dateutil.parser import parse
from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import MemberLoginForm, AdminLoginForm, RegistrationForm, SearchForm
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


@app.route('/event', methods=['GET', 'POST'])
def show_events():
	form = SearchForm()
	if form.is_submitted():
		search_type = form.search_type.data
		keyword = str(form.keyword.data).strip()
		if keyword is not None:
			return render_template('event.html', title='Events', form=form,
								   event_list=get_events(search_type, keyword))

	return render_template('event.html', title='Events',
						   form=form, event_list=get_events())


def get_events(search_type=None, keyword=None):
	records = None
	if keyword is None:
		records = db.session.query(Event, EventSlot).\
			join(EventSlot, Event.event_id == EventSlot.event_id).\
			order_by(Event.event_id).all()
	elif search_type == 'title':
		records = db.session.query(Event, EventSlot).\
			join(EventSlot, Event.event_id == EventSlot.event_id).\
			filter(Event.event_title.ilike(f'%{keyword}%')).\
			order_by(Event.event_id).all()
	else:
		#temporarily search all for other search_types
		records = db.session.query(Event, EventSlot).\
			join(EventSlot, Event.event_id == EventSlot.event_id).\
			order_by(Event.event_id).all()

	return format_events(records)


def format_events(records):
	event_list = []

	event = dict()
	for row in records:
		dt = parse(str(row.EventSlot.event_date))
		date = str(dt.date())
		time = str(dt.time().strftime('%H:%M'))

		if not bool(event) or row.Event.event_id != event['event_id']:
			add_to_list(event_list, event)
			event = { 'title' : row.Event.event_title,
					  'venue' : row.Event.venue,
					  'dates' : { date },
					  'times' : { time },
					  'duration' : row.Event.duration,
					  'capacity' : row.Event.capacity,
					  'type': row.Event.event_type,
					  'desc': row.Event.description,
					  'price' : row.Event.price,
					  'event_id' : row.Event.event_id }
		else:
			event['dates'].add(date)
			event['times'].add(time)

	add_to_list(event_list, event)
	return event_list


def add_to_list(event_list, event):
	if bool(event):
		event['dates'] = sorted(event['dates'])
		event['times'] = sorted(event['times'])
		event_list.append(event)
