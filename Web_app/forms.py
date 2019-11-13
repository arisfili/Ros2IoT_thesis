from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,IntegerField
from wtforms.validators import DataRequired, Length,  EqualTo
import amqp_protocol

class RegistrationForm(FlaskForm):
    fullname = StringField('FullName',
                           validators=[DataRequired(), Length(min=5, max=20)])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class DeviceForm(FlaskForm):
    name = StringField('name',
                           validators=[DataRequired(), Length(min=5, max=20)])
    role = StringField('role')
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    ip = StringField('ip',validators=[DataRequired()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ConnectDevice(FlaskForm):
    devicename = StringField('DeviceName',
                           validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Connect')

class ChooseDevice(FlaskForm):
    devicename = StringField('DeviceName',
                             validators=[DataRequired()])
    submit = SubmitField('Monitor')

class BridgePublisher(FlaskForm):
    topicname = StringField('TopicName',
                             validators=[DataRequired()])
    devicename = StringField('DeviceName',
                             validators=[DataRequired()])
    topictype = StringField('TopicType',
                            validators=[DataRequired()])
    submit = SubmitField('Bridge')

class BridgeService(FlaskForm):
    servicename = StringField('ServiceName',
                             validators=[DataRequired()])
    devicename = StringField('DeviceName',
                             validators=[DataRequired()])
    servicetype = StringField('ServiceType',
                            validators=[DataRequired()])
    submit = SubmitField('Bridge')

class TerminateTopic(FlaskForm):
    topicname = StringField('TopicName',
                             validators=[DataRequired()])
    devicename = StringField('DeviceName',
                             validators=[DataRequired()])
    submit = SubmitField('Terminate')

class TerminateService(FlaskForm):
    servicename = StringField('ServiceName',
                             validators=[DataRequired()])
    devicename = StringField('DeviceName',
                             validators=[DataRequired()])
    submit = SubmitField('Terminate')


