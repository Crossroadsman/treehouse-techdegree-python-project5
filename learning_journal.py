#!/usr/bin/env python3

"""Learning Journal
The main application for the Learning Journal application
Created: 2018
Last Update: 2018-08-11
Author: Alex Koumparos
Modified by: Alex Koumparos
"""
import datetime
import logging

from flask import Flask, g, render_template, redirect, url_for, flash, abort
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flask_bcrypt import check_password_hash

import models
import forms

logging.basicConfig(
    filename='learning_journal.log',
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'qazwsxedcrfvtgbyhnujmikolp'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


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
    if current_user.is_authenticated:
        return redirect(url_for('list'))

    # user is not logged in
    bad_login_msg = "Your username or password was invalid"
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash(bad_login_msg, "error")
            logging.exception(bad_login_msg)
        else:
            if check_password_hash(user.password,
                                   form.password.data):
                login_user(user)
                flash("You successfully logged in", "success")
                return redirect(url_for('list'))
            else:
                flash(bad_login_msg, "error")
                logging.info(bad_login_msg)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You successfully logged out")
    return redirect(url_for('login'))


@app.route('/entries')
@login_required  # login_required must be innermost decorator (see docs)
def list():
    user = current_user._get_current_object()
    journal_entries = user.journal_entries.order_by(
        models.JournalEntry.learning_date.desc()
    )
    return render_template('index.html', journal_entries=journal_entries)


@app.route('/entries/<slug>')
@app.route('/details/<slug>')
@login_required
def details(slug):
    """Project instructions require a route `/details` (instruction number 4)
    and a route
    `/entries/<slug>` (listed in instruction number 2).
    These don't appear to have any difference in substance, so they both
    route to the details view.
    """
    try:
        entry = models.JournalEntry.get(
            models.JournalEntry.url_slug == slug
        )
    except models.DoesNotExist:
        msg = "Unable to find record with url_slug {}".format(slug)
        logging.exception(msg)
        abort(404)
        pass

    return render_template('detail.html', entry=entry)


@app.route('/entries/edit/<slug>', methods=['GET', 'POST'])
@app.route('/entry', methods=['GET', 'POST'])
@login_required
def add_edit(slug=None):
    form = None
    if slug is None:  # NEW ENTRY
        form = forms.NewEntryForm()
        if form.validate_on_submit():
            # form is valid
            if form.learning_date.data is None:
                learning_date = datetime.datetime.now()
            else:
                learning_date = form.learning_date.data

            # Create a journal entry (except tags)
            try:
                models.JournalEntry.create_journal_entry(
                    title=form.title.data,
                    learning_date=learning_date,
                    time_spent=form.time_spent.data,
                    what_learned=form.what_learned.data,
                    resources=form.resources.data,
                    user=current_user._get_current_object()
                )
            except ValueError:
                msg = "Invalid entry: duplicate value detected"
                logging.exception(msg)
                flash(msg, category='error')
                template = 'new.html'
                return render_template(template, form=form)
            entry = models.JournalEntry.get(
                models.JournalEntry.title == form.title.data
            )

            # Create tags
            tags = form.tags.data.split()
            for tag_name in tags:
                tag, _ = models.SubjectTag.get_or_create(
                    name=tag_name
                )
                # Create a many-to-many relationship between the tag and the
                # journal entry
                models.JournalEntry_SubjectTag.create(
                    journal_entry=entry,
                    subject_tag=tag
                )

            return redirect(url_for('list'))
        else:
            template = 'new.html'
    else:  # EDIT ENTRY
        try:
            entry = models.JournalEntry.get(
                models.JournalEntry.url_slug == slug)
        except models.DoesNotExist:
            msg = "{} was not found to be a valid url_slug".format(slug)
            logging.exception(msg)
            abort(404)
        else:
            jests = entry.journal_entry_subject_tags
            tags = []
            for jest in jests:
                tags.append(jest.subject_tag.name)
            tag_string = " ".join(tags)
            form = forms.EditEntryForm(
                title=entry.title,
                learning_date=entry.learning_date,
                time_spent=entry.time_spent,
                what_learned=entry.what_learned,
                resources=entry.resources,
                tags=tag_string
            )
            if form.validate_on_submit():
                # form is valid

                # update entry
                try:
                    entry.title = form.title.data
                    entry.learning_date = form.learning_date.data
                    entry.time_spent = form.time_spent.data
                    entry.what_learned = form.what_learned.data
                    entry.resouces = form.resources.data
                    entry.save()
                except models.IntegrityError:
                    msg = "Invalid entry: duplicate value detected"
                    logging.exception(msg)
                    flash(msg, category='error')
                    template = 'edit.html'
                    return render_template(template, form=form)

                # Create tags (and delete old ones)
                old_jests = models.JournalEntry_SubjectTag.select().where(
                    models.JournalEntry_SubjectTag.journal_entry == entry
                )
                for jest in old_jests:
                    jest.delete_instance()
                tags = form.tags.data.split()
                for tag_name in tags:
                    tag, _ = models.SubjectTag.get_or_create(
                        name=tag_name
                    )
                    # Create a many-to-many relationship between the tag and
                    # the journal entry
                    jest, _ = models.JournalEntry_SubjectTag.get_or_create(
                        journal_entry=entry,
                        subject_tag=tag
                    )

                return redirect(url_for('list'))
            else:
                # form is invalid
                pass
        # edit entry
        template = 'edit.html'
        # form

    return render_template(template, form=form)


@app.route('/entries/delete/<slug>')
@login_required
def delete_entry(slug):
    try:
        entry = models.JournalEntry.get(models.JournalEntry.url_slug == slug)
    except models.DoesNotExist:
        msg = "{} was not found to be a valid url_slug".format(slug)
        logging.exception(msg)
        abort(404)
    else:
        try:
            entry.delete_instance()
        except:
            logging.error("UNABLE TO delete_instance for {}".format(entry))
            raise
    return redirect(url_for('list'))


@app.route('/tags')
@login_required
def tags():
    tags = models.SubjectTag.select()
    return render_template('tags.html', tags=tags)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

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
