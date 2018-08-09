#!/usr/bin/env python3

"""Learning Journal
The main application for the Learning Journal application
Created: 2018
Last Update: 2018-08-09
Author: Alex Koumparos
Modified by: Alex Koumparos
"""
from flask import Flask, g, render_template
from flask_login import LoginManager, current_user, login_required

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


@app.route('/', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    return "login will go here"


@app.route('/entries')
@login_required  # login_required must be innermost decorator (see docs)
def list():
    return render_template('index.html')


@app.route('/entries/<slug>')
@app.route('/details/<slug>')
@login_required
def details(slug):
    """Project instructions require a route `/details` (instruction number 4)
    and a route
    `/entries/<slug>`.
    These don't appear to have any difference in substance, so they both
    route to the details view.
    """
    try:
        entry = models.JournalEntry.select().where(
            models.JournalEntry.url_slug == slug
        ).get()
    except:
        # need to define exception
        # need to abort(404)
        pass

    return render_template('detail.html', entry=entry)


@app.route('/entries/edit/<slug>', methods=['GET', 'POST'])
@app.route('/entry', methods=['GET', 'POST'])
@login_required
def add_edit(slug=None):
    form = None
    if slug is None:
        # add entry
        template = 'new.html'
    else:
        # edit entry
        template = 'edit.html'
    # form
    return render_template(template, form=form)


@app.route('/entries/delete/<slug>')
@login_required
def delete_entry(slug):
    return "This will be the delete entry route"

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
