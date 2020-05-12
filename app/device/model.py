from peewee import Model, InternalError
from playhouse.migrate import SqliteMigrator, migrate
from peewee import IntegerField, FloatField, CharField, PrimaryKeyField, TimestampField, TextField, fn
from app import db

class Device(Model):
    id = PrimaryKeyField(null=False)
    name = CharField(unique=True)
    ip = CharField(unique=True)
    login = CharField(null=True)
    password = CharField(null=True)
    protocol = CharField(null=True)
    #comment = TextField(null=True)
    platform_id = IntegerField(null=True)
    class Meta:
        table_name = 'devices'
        database = db

    # @property
    # def table(): Приводит к ошибкм в SqliteMigrator
    #     return Device._meta.table_name

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
        self.db.create_tables([Device, Platform, SysParams])
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