from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, IPAddress, Email, ValidationError, AnyOf

from app import app
import logging

logger = logging.getLogger(app.logger.name)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
        else:
            logger.debug("Good username: %s" % username.data)

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')
        else:
            logger.debug("Good email")

class AddSensorForm(FlaskForm):
    name = StringField('Sensor Name', validators=[DataRequired()])
    ip = StringField('Sensor IP', validators=[DataRequired(), IPAddress()])
    submit = SubmitField('Add Sensor')