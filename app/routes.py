from app import app, db, query
from app.models.users import User, Admin
from app.models.events import Event, EventSlot
from app.models.booking import Booking
from app.forms.forms import MemberLoginForm, StaffLoginForm, RegistrationForm, \
							SearchForm, BookingForm
from flask import render_template, redirect, url_for
from flask_login import current_user, login_user, logout_user
from app.views.utils import is_admin_user, is_staff_user
from dateutil.parser import parse


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
		#redirect to admin page using flask_admin(endpoint=admin)
		return redirect(url_for('admin.index'))

	# renders staff login page
	return render_template('staff_login.html', title='EBS: Admin', form=form)


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
		new_user = User(username=form.username.data,
						email=form.email.data,
						is_staff=False)
		new_user.set_password(form.password.data)
		db.session.add(new_user)
		db.session.commit()
		login_user(new_user)
		return redirect(url_for('index'))
	return render_template('register.html', title='EBS: Account Registration', form=form)



@app.route('/event/details')
def get_details():
	return redirect(url_for('event_details', eid='1'))


@app.route('/event/details/<eid>')
def event_details(eid):
	records = db.session.query(Event, EventSlot)\
						.join(EventSlot, Event.event_id == EventSlot.event_id)\
						.filter(Event.event_id == eid).order_by(EventSlot.event_date)
	event = query.format_events(records)
	return render_template('details.html', title='EBS: ' + event['title'],
						   event=event, is_admin=is_admin_user(),
						   add_admin_btn=(is_staff_user() or is_admin_user()))


@app.route('/booking/<eid>', methods=['GET', 'POST'])
def booking(eid):
	if not current_user.is_authenticated:
		return redirect(url_for('user_login'))
	elif is_admin_user():
		return redirect(url_for('event_details', eid=eid))

	selected_event = Event.query.get(eid)
	event_slots = db.session.query(EventSlot.event_date, EventSlot.slot_id)\
							.join(Event, EventSlot.event_id == Event.event_id)\
							.filter(EventSlot.event_id == eid).all()

	form = BookingForm()
	form.preload(current_user, selected_event, event_slots)
	if form.is_submitted():
		uid = current_user.user_id
		esid = form.date.data
		qty = form.count.data

		booking = Booking(user_id=uid, event_slot_id=esid, quantity=qty)
		db.session.add(booking)
		db.session.commit()

		return render_template('confirm_booking.html',
	   						   add_admin_btn=(is_staff_user() or is_admin_user()))

	return render_template('booking.html', form=form,
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
