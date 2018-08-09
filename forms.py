#!/usr/bin/env python3

"""Forms
The forms file for the Learning Journal application
Created: 2018
Last Update: 2018-08-09
Author: Alex Koumparos
Modified by: Alex Koumparos
"""
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from models import User


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
