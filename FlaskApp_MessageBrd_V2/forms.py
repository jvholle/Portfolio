from flask_wtf import FlaskForm as form
from wtforms import StringField, SelectField, HiddenField, DateField, DateTimeField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, InputRequired, Optional, Email
import time
import datetime
from MessBrd_Postgres_V2 import models

# query user to add a claim
class ChooseName(form):
    name = SelectField('Choose Name')  #, choices=[(i, i) for i in Item.trType])

# date picker form
class DatePick(form):
    dates = SelectField('Pick Date')  #, default='None', validators=[DataRequired(message='Choose a Date')])

# Add comment.
class AddComment(form):
    #iDate = datetime.datetime.now()  # convert time object to string. date_str = iDate.strftime('%Y-%m-%d')

    firstname = StringField('Name', validators=[Optional()])
    comment = TextAreaField('Comment', validators=[DataRequired()], render_kw={"rows": 10, "cols": 50})
    date = DateTimeField('Date', default=datetime.datetime.today, format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])  # stores a datetime.date ,
    user_id = StringField('User ID', validators=[DataRequired()], render_kw={'readonly': True})
    email = StringField('Email', validators=[Optional()], render_kw={'readonly': True})

# Insert a response comment.
class RespComment(form):
    #iDate = datetime.datetime.now()  # convert time object to string. date_str = iDate.strftime('%Y-%m-%d')

    firstname = StringField('Name', validators=[Optional()])
    origcomment = TextAreaField('Original Comment', validators=[DataRequired()], render_kw={"rows": 6, "cols": 50})
    comment = TextAreaField('Response', validators=[DataRequired()], render_kw={"rows": 6, "cols": 50})
    date = DateTimeField('Date', default=datetime.datetime.today, format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])  # stores a datetime.date ,
    #user_id = StringField('User ID', validators=[DataRequired()], render_kw={'readonly': True})
    responseto = StringField('Responseto', validators=[DataRequired()], render_kw={'readonly': True})
    responsedate = DateTimeField('Comment Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])

# Insert a Claim into the claim table.
class InitLogin(form):
    #iDate = datetime.datetime.now()  # convert time object to string. date_str = iDate.strftime('%Y-%m-%d')

    firstname = StringField('First Name', validators=[Optional()])
    email = StringField('Email', validators=[DataRequired(), Email(message='Must be proper email format!')])
    # user_pw = PasswordField('Password', validators=[DataRequired()])

# Register user.
class Register(form):
    firstname = StringField('First Name', validators=[])
    lastname = StringField('Last Name', validators=[])
    email = StringField('Email', validators=[DataRequired(), Email(message='Must be proper email format!')])
    password = PasswordField('Password', validators=[DataRequired()])