from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

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

    def __init__(self, username, password):
        self.username = username
        self.password = password

# create tables
Base.metadata.create_all(engine)
