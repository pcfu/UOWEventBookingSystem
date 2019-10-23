from flask import Flask
from app.config import Config
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.menu import MenuLink

convention = {
	"ix": 'ix_%(column_0_label)s',
	"uq": "uq_%(table_name)s_%(column_0_name)s",
	"ck": "ck_%(table_name)s_%(column_0_name)s",
	"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
	"pk": "pk_%(table_name)s"
}


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app, metadata=MetaData(naming_convention=convention)) # DB instance
migrate = Migrate(app, db, render_as_batch=True) # Flask database migration manager
login_manager = LoginManager(app) # Flask login_manager


#Create admin with restricted view access
from app import models, routes
from app import views

admin = Admin(app, name='UOW Event System', template_mode='bootstrap3',
			  index_view=views.NoBypassAdminView())
admin.add_view(views.NoBypassModelView(models.User, db.session))
admin.add_view(views.NoBypassModelView(models.Event, db.session))
admin.add_view(views.NoBypassModelView(models.EventSlot, db.session))
admin.add_link(MenuLink(name='logout', category='', url='/logout'))
