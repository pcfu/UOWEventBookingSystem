from flask import Flask
from app.config import Config
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


# Create the main app object that is called by event_system.py
app = Flask(__name__)
app.config.from_object(Config)


# Create database
convention = {
	"ix": 'ix_%(column_0_label)s',
	"uq": "uq_%(table_name)s_%(column_0_name)s",
	"ck": "ck_%(table_name)s_%(column_0_name)s",
	"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
	"pk": "pk_%(table_name)s"
}

db = SQLAlchemy(app, metadata=MetaData(naming_convention=convention)) # DB instance
migrate = Migrate(app, db, render_as_batch=True) # Flask database migration manager


# Create login manager
login_manager = LoginManager(app) # Flask login_manager


from app import routes
