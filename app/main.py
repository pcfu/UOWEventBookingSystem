import os
import app.account as account
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from sqlalchemy.orm import sessionmaker
from app.database_table_definitions import *

#engine = create_engine('sqlite:///csit214_database.db', echo=True)
app = Flask(__name__)

"""
All the routes are kinda like url, so if /login -> localhost:4000/login
For now this program allows you to create users and store it in a csit214_database.db file and allows logging in
if the entered credentials are correct

Todo implementations are -
Creating Event class, creating dummy events and displaying them in a /showevent page or something
"""


# For now / renders the login.html template which is the login screen if you are not already logged in
@app.route('/')
def home():
	if not session.get('logged_in'):
		return render_template('login.html', page_title='CSIT214 Group Work')
	else:
		return "Hello Boss! <a href='/logout'>Logout</a> <a href='/events'>View Events</a>"


# This function checks if the entered username and password is valid or not from the entries
# POST_U/P is received from the form's input elements by it's NAME (presumably, not sure)
# the values are then passed into a database session query for the user and sets this current program instance
# to logged in if entered details are correct.
# This function is invoked via a form action='/login' in the html with the use of a input type=submit
@app.route('/login', methods=['POST'])
def user_login():
	POST_USERNAME = str(request.form['username'])
	POST_PASSWORD = str(request.form['password'])
	Session = sessionmaker(bind=engine)
	s = Session()
	query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]))
	result = query.first()
	if result:
		session['logged_in'] = True
	else:
		flash('wrong password!')
	return redirect(url_for('home'))


# Invoked when "Admin Login" is selected
@app.route('/admin', methods=['GET', 'POST'])
def admin_login_page():
	return render_template('admin.html')


# Admin homepage
@app.route('/admin_home')
def admin_home():
	if not session.get('logged_in'):
		return render_template('/', page_title='CSIT214 Group Work')
	else:
		return "Hello admin! <a href='/logout'>Logout</a>"


# Invoked when login form is submitted in /admin.html
@app.route('/admin_login', methods=['POST'])
def admin_login():
	POST_USERNAME = str(request.form['username'])
	POST_PASSWORD = str(request.form['password'])
	Session = sessionmaker(bind=engine)
	s = Session()
	query = s.query(Admin).filter(Admin.username.in_([POST_USERNAME]), Admin.password.in_([POST_PASSWORD]))
	result = query.first()
	if result:
		session['logged_in'] = True
	else:
		flash('wrong password!')
	return redirect(url_for('admin_home'))


@app.route('/logout')
def logout():
	session['logged_in'] = False
	return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	return render_template('register.html', page_title='Account Registration')


@app.route('/auth', methods=['POST'])
def authenticate():
	USERNAME = str(request.form['username'])
	PASSWORD = str(request.form['password'])
	CONFIRM_PW = str(request.form['confirm-pw'])

	session = sessionmaker(bind=engine)
	error = account.validate(USERNAME, PASSWORD, CONFIRM_PW, session())
	if error:
		flash(error)
		return redirect(url_for('register'))
	else:
		account.create_acct(USERNAME, PASSWORD, session())
		flash('Account registered. Welcome ' + USERNAME + '!')
		return redirect(url_for('home'))

@app.route('/events')
def test():
	Session = sessionmaker(bind=engine)
	s = Session()
	x = ''
	for row in s.query(Event):
		x = row.to_string()
		flash(x)
	return render_template('event.html')


if __name__ == '__main__':
    app.secret_key = os.urandom(12) #Need this for session to work
    app.run(debug=True, port=4000)

