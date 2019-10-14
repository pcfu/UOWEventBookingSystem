from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
import datetime

"""
Database-table objects are created here - a defined User class belongs to a pre-determined table called "users"
with attributes id, username and password - while the constructor takes in the latter 2. Eventually the User should be
identified as admin/non admin in some sense or another

In the near future i think there will be an Event class to create events

The classes here are defined and invoked in other files - for now make_user_accounts imports this and creates User objs
"""

engine = create_engine('sqlite:///csit214_database.db', echo=True)
Base = declarative_base()


########################################################################
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    def __init__(self, username: str, password: str):

        self.username = username
        self.password = password


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    def __init__(self, id:int, username: str, password: str):
        self.id = id
        self.username = username
        self.password = password


class Event(Base):
    __tablename__ = "events"
    event_id = Column(Integer, primary_key=True)
    event_title = Column(String)
    dt_start = Column(DateTime)
    dt_end = Column(DateTime)
    created_by = Column(String) #FK1 - Admin username
    price = Column(Integer)

    def __init__(self, event_id: int, event_title: str, dt_start: datetime, dt_end: datetime, created_by: str, price: int):
        self.event_id = event_id
        self.event_title = event_title
        self.dt_start = dt_start
        self.dt_end = dt_end
        self.created_by = created_by
        self.price = price

    def to_string(self):
        return "Event ID: {}\n" \
               "Event Title: {}\n" \
               "Organizer: {}".format(self.event_id, self.event_title, self.created_by)


class Participation(Base):
    __tablename__ = "participations"
    event_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)

    def __init__(self, event_id: int, user_id: int):
        self.event_id = event_id
        self.user_id = user_id


# create tables
Base.metadata.create_all(engine)
