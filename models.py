import peewee
import datetime
from database import db


class User(peewee.Model):
    email = peewee.CharField(unique=True, index=True)
    username = peewee.CharField(unique=True, index=True)
    full_name= peewee.CharField()
    hashed_password = peewee.CharField()
    verified = peewee.BooleanField(default=True)

    class Meta:
        database = db


class Todo(peewee.Model):
    todo = peewee.CharField(index=True)
    isDone = peewee.BooleanField(index=True, default=False)
    created_at = peewee.DateTimeField(formats='%Y-%m-%d %H:%M:%S', default=datetime.datetime.now)
    completed_at = peewee.DateTimeField(formats='%Y-%m-%d %H:%M:%S', null=True)
    set_completed_at = peewee.DateTimeField(formats='%Y-%m-%d %H:%M:%S', null=True)
    owner = peewee.ForeignKeyField(User, backref="todos")

    class Meta:
        database = db
