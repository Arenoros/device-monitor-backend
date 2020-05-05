from peewee import Model
from peewee import IntegerField, FloatField, CharField, PrimaryKeyField, TimestampField, fn
from app import db

class Device(Model):
    id = PrimaryKeyField(null=False)
    name = CharField(unique=True)
    ip = CharField(unique=True)
    login = CharField()
    password = CharField()
    platform_id = IntegerField()
    
    class Meta:
        db_table = 'devices'
        database = db

