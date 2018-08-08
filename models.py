#!/usr/bin/env python3

"""Models
The Database models for the Learning Journal application
Created: 2018
Last Update: 2018-08-08
Author: Alex Koumparos
Modified by: Alex Koumparos
"""
import datetime

from peewee import *
from flask_bcrypt import generate_password_hash
from flask_bcrypt import check_password_hash
from flask_login import UserMixin


SECRET_KEY = 'qazwsxedcrfvtgbyhnujmikolp'

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

DATABASE = SqliteDatabase('learning_journal.db')


class User(UserMixin, Model):
    """The User, enables multiple people to privately use the same instance
    of Learning Journal"""
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password):
        """Create a User and write it to the database."""
        with DATABASE.transaction():
            try:
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password)
                )
            except IntegrityError:
                raise ValueError("User already exists")


class JournalEntry(Model):
    """The main Model class for the application."""

    """In order to meet the specifications of the project for route
    names, titles are currently set to be unique. To make this application
    truly multi-user for production, we would change the routes so that
    the url for every journal entry would include the user's username so
    that multiple users could have journal entries with the same name,
    then we could remove the unique requirement for title"""
    title = CharField(unique=True)
    created_date = DateTimeField(default=datetime.datetime.now)
    url_slug = TBD
    time_spent = IntegerField()  # minutes
    what_learned = TextField()
    resources = TextField()
    """Note that the syntax for initialising a ForeignKeyField has changed
    in peewee 3.0 (see the backwards incompatible section at:
    http://docs.peewee-orm.com/en/latest/peewee/changes.html)
    particularly:
    rel_model -> model
    related_name -> backref
    """
    user = ForeignKeyField(
        model=User,
        backref='journal_entries'
    )

    class Meta:
        database = DATABASE
        # `-` indicates descending order
        order_by = ('-created_date',)


class SubjectTag(Model):
    """Tags for particular subjects. Many-to-many with JournalEntry because
    multiple journal entries can have a particular tag, and a journal entry
    can have multiple tags.
    """
    name = CharField(unique=True)
    journal_entries = TBD


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User], safe=True)
    DATABASE.close()
