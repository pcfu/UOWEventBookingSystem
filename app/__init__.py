from flask import Flask
from app.config import Config
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.menu import MenuLink


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
from app.models import users, events, booking
from app.views import views


admin = Admin(app, name='UOW Event System', template_mode='bootstrap3',
			  index_view=views.GlobalIndexView())
admin.add_view(views.StaffVenueView(events.Venue, db.session))
admin.add_view(views.StaffEventTypeView(events.EventType, db.session))
admin.add_view(views.StaffEventView(events.Event, db.session))
admin.add_view(views.StaffEventSlotView(events.EventSlot, db.session))
admin.add_view(views.StaffBookingView(booking.Booking, db.session))
admin.add_view(views.AdminUserView(users.User, db.session))
admin.add_link(MenuLink(name='front page', category='', url='/'))
admin.add_link(MenuLink(name='logout', category='', url='/logout'))
