import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database_table_definitions import *

'''
This file has to be run manually to create the user names into user_accounts.db
Only have to run 1 time to create the below sample user objects into the .db file

Eventually there might or might not have some sort of user creation function
'''

engine = create_engine('sqlite:///csit214_database.db', echo=True)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

"""
user = User("admin","password")
session.add(user)

user = User("python","python")
session.add(user)

user = User("jumpiness","python")
session.add(user)
"""

admin = Admin(1, "testadmin", "password1")
session.add(admin)
# commit the record the database
session.commit()

session.commit()
