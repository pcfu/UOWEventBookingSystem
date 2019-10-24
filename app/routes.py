from dateutil.parser import parse
from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import MemberLoginForm, AdminLoginForm, RegistrationForm, SearchForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Staff, Event, EventSlot

# url_for will ALWAYS be function name
"""
Now because of User and Staff being 2 different tables but with the same primary key counter
i.e. User has ID1 and so does Staff, the login authentication fails in the sense that admin will be able to access
admin page via url insertion.

User login returns you to some temp page, while Staff login returns you to the dashboard for Flask_Admin
however, flask_login determines the user to be user1 regardless of admin or user because user.loader queries for User table
so meaning to say user2 with ID2, and admin2 with ID2 - if logged in as admin2, flask_login identifies you as user2

There is also an issue with circular inclusion in models.py which i have explained there
For now the NewEventForm and new event routes are not required anymore because Flask_Admin allows us to create new rows in the DB
"""

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
	records = db.session.query(Event, EventSlot).\
		join(EventSlot, Event.event_id == EventSlot.event_id).all()

	event_list = []
	for row in records:
		dt = parse(str(row.EventSlot.event_date))
		event_list.append({ 'title' : row.Event.event_title,
							'venue' : row.Event.venue,
							'date' : dt.date(),
							'time' : dt.time().strftime('%I:%M %p'),
							'duration' : row.Event.duration,
							'capacity' : row.Event.capacity,
							'type': row.Event.event_type,
							'desc': row.Event.description,
							'price' : row.Event.price,
							'slot_id' : row.EventSlot.slot_id })

	form = SearchForm()

	return render_template('event.html', title='Events',
						   form=form, event_list=event_list)
