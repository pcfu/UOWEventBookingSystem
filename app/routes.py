from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import MemberLoginForm, AdminLoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Staff, Event

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
		#consider display staff username natively from admin.index instead of flash
		flash('logged in as {}'.format(staff.username))
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
	data = Event.query.all()
	return render_template('event.html', title='Events', rows=data)

#obsolete for now
@app.route('/new_event')
def new_event():
	new_event_form = NewEventForm()
	return render_template('event/new.html', form=new_event_form)
