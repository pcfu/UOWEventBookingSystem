from flask import session
from sqlalchemy.orm import sessionmaker
from app.models import *


def validate(name: str, passwd: str, confirm_pw: str, session: session) -> str:
    if len(name) == 0:
        return 'Please enter a username'
    elif is_taken_name(name, session):
        return 'An account with this username has already been created'
    elif len(passwd) < 8:
        return 'Password must be at least 8 characters long'
    elif passwd != confirm_pw:
        return 'Passwords do not match'
    else:
        return ''


def is_taken_name(name: str, session: session):
    query = session.query(User).filter(User.username.in_([name]))
    return bool(query.first())


def create_acct(name: str, passwd: str, session: session):
    user = User(name, passwd)
    session.add(user)
    session.commit()
