from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.database_table_definitions import Event
import datetime

engine = create_engine('sqlite:///csit214_database.db', echo=True)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()


test_event = Event(2, "Test Event 2", datetime.datetime.now(), datetime.datetime.now(), "testadmin", 0)

session.add(test_event)
session.commit()