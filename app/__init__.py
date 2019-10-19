from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) # DB instance
migrate = Migrate(app, db) # Flask database migration(updating) manager
login_manager = LoginManager(app) # Flask login_manager
admin = Admin(app, endpoint='admin', name='UOW Event System') # Flask_Admin manager, endpoint is the url

from app import models, routes

