from sqlalchemy import ForeignKey
from app import db, login_manager, admin
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView



@login_manager.user_loader()
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(255), unique=True)

    # This is a replacement for tostring
    def __repr__(self):
        return '<Username: {}>'.format(self.username)

    def get_id(self):
        return self.user_id


class Staff(UserMixin, db.Model):
    __tablename__ = 'staff'
    staff_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(255), unique=True)
    events = db.relationship('Event', backref='creator', lazy='dynamic')

    def __repr__(self):
        return '<Username: {}>'.format(self.username)

    def get_id(self):
        return self.staff_id

class Event(db.Model):
    __tablename__ = 'event'
    event_id = db.Column(db.Integer, primary_key=True)
    event_title = db.Column(db.String, nullable=False)
    venue = db.Column(db.String, nullable=False)
    capacity = db.Column(db.Integer)
    type = db.Column(db.String)
    description = db.Column(db.String)
    created_by = db.Column(db.Integer, ForeignKey('staff.staff_id'))
    price = db.Column(db.Integer)

    def __repr__(self):
        return "Event ID: {}\n" \
               "Event Title: {}\n" \
               "Organizer: {}".format(self.event_id, self.event_title, self.created_by)


class EventSlot(db.Model):
    __tablename__ = 'eventslot'
    event_id = db.Column(db.Integer, ForeignKey('event.event_id'), primary_key=True)
    event_date = db.Column(db.DateTime, primary_key=True)

    def __repr__(self):
        return "ID: {}\nDate:".format(self.event_id, self.event_date)


class Booking(db.Model):
    booking_no = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.user_id'), unique=True)
    event_id = db.Column(db.Integer, ForeignKey('event.event_id'), unique=True)
    event_date = db.Column(db.DateTime, ForeignKey('eventslot.event_date'), unique=True)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "Booking No: {}\nUserID: {}".format(self.booking_no, self.user_id)


# this is supposed to be placed inside __init__ but because of circular inclusion for models and init i cant do it
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Event, db.session))
