from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password',
                                                                                             message='Password must match!')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken')

    def validate_email(self, email):
        user = User.query_filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already taken')


class NewEventForm(FlaskForm):
    event_title = StringField('Title', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired])
    price = IntegerField('Price', validators=[DataRequired()])
    submit = SubmitField('Create Event')
