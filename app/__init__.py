from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.menu import MenuLink


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) # DB instance
migrate = Migrate(app, db) # Flask database migration(updating) manager
login_manager = LoginManager(app) # Flask login_manager


#Create admin with restricted view access
from app import models, routes
from app import views

admin = Admin(app, name='UOW Event System', template_mode='bootstrap3',
			  index_view=views.NoBypassAdminView())
admin.add_view(views.NoBypassModelView(models.User, db.session))
admin.add_view(views.NoBypassModelView(models.Event, db.session))
admin.add_link(MenuLink(name='logout', category='', url='/logout'))
