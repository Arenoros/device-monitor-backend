from peewee import Model, InternalError
from playhouse.migrate import SqliteMigrator, migrate
from peewee import IntegerField, FloatField, CharField, PrimaryKeyField, TimestampField, TextField, fn
from app import db

class Device(Model):
    name = CharField(unique=True)
    login = CharField(null=False)
    password = CharField(null=True)
    protocol = CharField(null=True)
    port = IntegerField(null=True)
    host_id = IntegerField(null=True)
    platform_id = IntegerField(null=True)
    class Meta:
        table_name = 'devices'
        database = db

    # @property
    # def table(): Приводит к ошибкм в SqliteMigrator
    #     return Device._meta.table_name

class Host(Model):
    ip = CharField(unique=True)
    room = CharField(null=False)
    class Meta:
        table_name = 'hosts'
        database = db

class ConnectedControllers(Model):
    host_id = IntegerField()
    controller_id = IntegerField()
    class Meta:
        table_name = 'connected_controllers'
        indexes = (
            (('host_id', 'controller_id'), True),  # Note the trailing comma!
        )

class Platform(Model):
    name = CharField(null=False)
    settings = TextField()
    meta = TextField()

    class Meta:
        table_name = 'platforms'
        database = db

class SysParams(Model):
    name = CharField(unique=True)
    value = CharField()
    class Meta:
        table_name = 'sys_params'
        database = db
    
class DeviceDbMigrations:
    migrator = SqliteMigrator(db)
    migrations = [
       #migrator.add_column(Device._meta.table_name, Device.comment.name, Device.comment)
    ]
    cur_version=len(migrations)
    version_field = 'schema_version'

    def createAll(self):
        self.db.create_tables([Device, Host, ConnectedControllers, Platform, SysParams])
        sh_v = SysParams.create(
            name=self.version_field, 
            value=str(self.cur_version)
        )
        sh_v.save()

    def run(self):
        if SysParams._meta.table_name not in self.db.get_tables():
            return self.createAll()
        res = SysParams.get(SysParams.name == self.version_field)
        db_version = int(res.value)
        migrate(*self.migrations[db_version:])
        SysParams.update(value=str(self.cur_version)).where(SysParams.name == self.version_field)

    def __init__(self, db):
        self.db = db

try:
    db.connect()
    migration = DeviceDbMigrations(db)
    migration.run()
except InternalError as px:
    print(str(px))