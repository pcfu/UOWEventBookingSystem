from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, NewEventForm
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
	return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def user_login():
	# if already logged in redirect to homepage
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = LoginForm()
	if form.validate_on_submit():
		# if login is successful, return user to 'index'
		user = User.query.filter_by(username=form.username.data).first()
		login_user(user, remember=form.remember_me.data)
		return redirect(url_for('index'))

	# render login page
	return render_template('login.html', title='Sign In', form=form)


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


@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
	# if already logged in redirect to homepage
	form = LoginForm()
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	# if submit is selected on form - checks if user exist in database
	if form.validate_on_submit():
		staff = Staff.query.filter_by(username=form.username.data).first()
		if staff is None: #or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('staff_login'))
		# if login is successful, return staff to 'index'
		login_user(staff)
		flash('logged in as: {}'.format(staff.username))
		return redirect(url_for('admin.index')) #redirects to admin page using flask_admin(endpoint=admin)
	# renders this when called
	return render_template('staff_login.html', title='Admin Sign In', form=form)


@app.route('/event')
def show_events():
	data = Event.query.all()
	return render_template('event.html', rows=data)

#obsolete for now
@app.route('/new_event')
def new_event():
	new_event_form = NewEventForm()
	return render_template('event/new.html', form=new_event_form)
