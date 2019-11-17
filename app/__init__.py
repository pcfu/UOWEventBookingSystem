from flask import Flask, session
from app.config import Config
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_session import Session
#from flask_apscheduler import APScheduler
from flask_admin import Admin
from flask_admin.menu import MenuLink
import warnings
import os


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


# Set up session
Session(app)


'''
# Create scheduler (conditional prevents scheduler from initialising twice)
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
	scheduler = APScheduler()
	scheduler.init_app(app)
	scheduler.start()
'''


from app import routes
from app.models import users, logs, events #, booking, payments
from app.views import views


# Create admin
admin = Admin(app, name='UOW EBS', template_mode='bootstrap3',
			  index_view=views.GlobalIndexView())

'''
# Add staff views
admin.add_view(views.StaffVenueView(events.Venue, db.session, category='Events'))
admin.add_view(views.StaffEventTypeView(events.EventType, db.session, category='Events'))
with warnings.catch_warnings():
	warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
	admin.add_view(views.StaffEventView(events.Event, db.session, category='Events'))
	admin.add_view(views.StaffEventSlotView(events.EventSlot, db.session, category='Events'))
	admin.add_view(views.StaffPromotionView(payments.Promotion, db.session, category='Promotions'))

admin.add_view(views.StaffEventPromoView(payments.EventPromotion, db.session, category='Promotions'))
admin.add_view(views.StaffBookingView(booking.Booking, db.session))
admin.add_view(views.StaffPaymentView(payments.Payment, db.session, category='Payments'))
admin.add_view(views.StaffRefundView(payments.Refund, db.session, category='Payments'))
'''

# Add administrator views
with warnings.catch_warnings():
	warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
	admin.add_view(views.AdminUserView(users.User, db.session))
admin.add_view(views.AdminLoginHistoryView(logs.LoginHistory, db.session))
admin.add_view(views.AdminLogoutHistoryView(logs.LogoutHistory, db.session))

# Add extra navbar links
admin.add_link(MenuLink(name='front page', category='', url='/'))
admin.add_link(MenuLink(name='logout', category='', url='/logout'))
