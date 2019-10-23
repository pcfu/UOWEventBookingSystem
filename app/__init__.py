from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) # DB instance
migrate = Migrate(app, db) # Flask database migration(updating) manager
login_manager = LoginManager(app) # Flask login_manager


#Create admin with restricted index access
from app import models
from app import views

admin = Admin(app, name='UOW Event System', template_mode='bootstrap3',
			  index_view=views.RestrictedAdminIndexView())
admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Event, db.session))
