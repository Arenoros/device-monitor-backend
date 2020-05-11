from peewee import SqliteDatabase, InternalError
from flask import  Flask, request, render_template, redirect
from flask_restful import Resource, Api

app = Flask(__name__)
app.config.from_object('config')

db = SqliteDatabase('storage/devices.db')


@app.errorhandler(404)
def not_found(error):
    return '<h1>404</h1>', 404 #render_template('404.html'), 404

# Import a module / component using its blueprint handler variable (mod_auth)
from app.device import mod_devices as devices_module
from app.device.model import Device, SysParams, Platform
from peewee import Model

@app.route('/api')
def index():
    return '<h1> FINALY</h1>'
    return redirect(devices_module)

# Register blueprint(s)
app.register_blueprint(devices_module, url_prefix='/api/devices')

try:
    db.connect()
    db.create_tables(SysParams)
    #db.create_tables([Device, Platform, SysParams])
except InternalError as px:
    print(str(px))