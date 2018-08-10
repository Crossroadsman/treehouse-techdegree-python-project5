#!/usr/bin/env python3

"""Forms
The forms file for the Learning Journal application
Created: 2018
Last Update: 2018-08-10
Author: Alex Koumparos
Modified by: Alex Koumparos
"""
from flask_wtf import Form
from wtforms import (StringField, PasswordField, DateTimeField,
                     IntegerField, TextAreaField)
from wtforms.validators import DataRequired, Optional

from models import User, JournalEntry


# Custom Validators


# Forms
class LoginForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ]
    )

class NewEntryForm(Form):
    title = StringField(
        'Title',
        validators=[
            DataRequired()
        ]
    )
    learning_date = DateTimeField(
        'Date (or leave blank to use the current date and time)',
        validators=[
            Optional()
        ],
        render_kw={"placeholder": "yyyy-mm-dd hh:mm:ss"}
    )
    time_spent = IntegerField(
        'Time spent (in minutes)',
        validators=[
            DataRequired()
        ]
    )
    what_learned = TextAreaField(
        'What I Learned',
        validators=[
            DataRequired()
        ]
    )
    resources = TextAreaField(
        'Resources to Remember',
        validators=[
            DataRequired()
        ]
    )
    tags = StringField(
        'Tags (space separated)',
        validators=[]
    )

class EditEntryForm(Form):
    title = StringField(
        'Title',
        validators=[
            DataRequired()
        ]
    )
    learning_date = DateTimeField(
        'Date (or leave blank for now)',
        validators=[
            Optional()
        ]
    )
    time_spent = IntegerField(
        'Time spent (in minutes)',
        validators=[
            DataRequired()
        ]
    )
    what_learned = TextAreaField(
        'What I Learned',
        validators=[
            DataRequired()
        ]
    )
    resources = TextAreaField(
        'Resources to Remember',
        validators=[
            DataRequired()
        ]
    )