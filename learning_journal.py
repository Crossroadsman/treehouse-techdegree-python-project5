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


DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'qazwsxedcrfvtgbyhnujmikolp'

login_manager = LoginManager()
login_manager.init_app(app)
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

"""
routes:

'/'

'/entries'

'/entries/<slug>'

'/entries/edit/<slug>'

'/entries/delete/<slug>'

'/entry'
"""

# ------------------------

if __name__ == '__main__':
    pwd = "password"
    models.initialize()
    try:
        models.User.create_user(
            username="testuser",
            email="test@example.com",
            password="password"
        )
    except ValueError:
        # user already exists so don't need to recreate
        pass
    app.run(
        debug=DEBUG,
        host=HOST,
        port=PORT
    )