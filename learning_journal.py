#!/usr/bin/env python3

"""Learning Journal
The main application for the Learning Journal application
Created: 2018
Last Update: 2018-08-08
Author: Alex Koumparos
Modified by: Alex Koumparos
"""
from flask import Flask, g
from flask_login import LoginManager, current_user

import models


app = Flask(__name__)
app.secret_key = 'qazwsxedcrfvtgbyhnujmikolp'

login_manager = LoginManager()
login_manager.init.app(app)
login_manager.login_view = 'login'

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response