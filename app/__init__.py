from flask import Flask, redirect, url_for
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) # DB instance
migrate = Migrate(app, db) # Flask database migration(updating) manager
login_manager = LoginManager(app) # Flask login_manager


from app import models, routes

class RestrictedAdminIndexView(AdminIndexView):
	@expose('/')
	def index(self):
		staff = None
		if current_user.is_authenticated:
			staff = models.Staff.query.filter_by(username=current_user.username).first()

		if staff is not None:
			return self.render('/admin/index.html')
		else:
			return redirect(url_for('staff_login'))

#admin = Admin(app, endpoint='admin', name='UOW Event System') # Flask_Admin manager, endpoint is the url
admin = Admin(app, name='UOW Event System', template_mode='bootstrap3',
			  index_view=RestrictedAdminIndexView())
admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Event, db.session))
