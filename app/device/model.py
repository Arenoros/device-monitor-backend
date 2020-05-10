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

class Platform(Model):
    id = PrimaryKeyField(null=False)
    os = CharField(null=False)
    os_v = CharField()
    arch = CharField(null=False)
    libc = CharField()
    libc_v = CharField()
    stdlib = CharField()
    stdlib_v = CharField()
    target = CharField()
    compiler = CharField()
    compiler = CharField()

    class Meta:
        db_table = 'platforms'
        database = db

