from peewee import SqliteDatabase, InternalError 
from flask import  Flask, request, render_template, redirect
from flask_restful import Resource, Api

app = Flask(__name__)
app.config.from_object('config')

db = SqliteDatabase('storage/devices.db')


@app.errorhandler(404)
def not_found(error):
    return '404', 404 #render_template('404.html'), 404

# Import a module / component using its blueprint handler variable (mod_auth)
from app.device import mod_devices as devices_module

@app.route('/')
def index():
    return redirect(devices_module.url_prefix)

# Register blueprint(s)
app.register_blueprint(devices_module)

try:
    db.connect()
    db.create_tables([device.model.Device])
except InternalError as px:
    print(str(px))