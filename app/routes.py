from app import app
from flask import render_template, redirect, url_for


@app.login_manager.user_loader
def load_user(entry):
	return True


@app.route('/')
@app.route('/index')
@app.route('/search')
def index():
	return render_template('base.html', title='Event Booking System')


@app.route('/login', methods=['GET', 'POST'])
def user_login():
	return redirect(url_for('index'))


@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
	return redirect(url_for('index'))


@app.route('/logout')
def logout():
	#logout_user()
	return redirect(url_for('main'))
