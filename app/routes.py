from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, NewEventForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Staff

# url_for will ALWAYS be function name


@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def user_login():
	# if already logged in redirect to homepage
	form = LoginForm()
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	# if submit is selected on form - checks if user exist in database
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None: #or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('user_login'))
		# if login is successful, return user to 'index'
		login_user(user, remember=form.remember_me.data)
		flash('logged in as: {}'.format(user.username))
		return redirect(url_for('index'))
	# renders this when called
	return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	registration_form = RegistrationForm()
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	if registration_form.validate_on_submit():
		user = User(username=registration_form.username.data, password=registration_form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('User created: {}'.format(user.username))
		return redirect(url_for('index'))
	return render_template('register.html', page_title='Account Registration', form=registration_form)


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
		return redirect(url_for('staff_home'))
	# renders this when called
	return render_template('staff_login.html', title='Admin Sign In', form=form)

@app.route('/staff_home')
def staff_home():
	return render_template('staff_home.html')

@app.route('/new_event')
def new_event():
	new_event_form = NewEventForm()
	print(current_user)
	return render_template('event/new.html', form=new_event_form)
