from app import db
from app.models.logs import LoginHistory, LogoutHistory
from flask_login import current_user
from datetime import datetime


def add_login_record():
	log = LoginHistory(timestamp=datetime.now(), user_id=current_user.user_id)
	db.session.add(log)
	db.session.commit()


def add_logout_record():
	log = LogoutHistory(timestamp=datetime.now(), user_id=current_user.user_id)
	db.session.add(log)
	db.session.commit()
