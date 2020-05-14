from peewee import SqliteDatabase, InternalError
from flask import  Flask, request, render_template, redirect, make_response, jsonify, abort
from flask_restful import Resource, Api

app = Flask(__name__)
app.config.from_object('config')

db = SqliteDatabase('storage/devices.db')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': error}), 404)

# Import a module / component using its blueprint handler variable (mod_auth)
from app.device import mod_devices as devices_module
from app.device.model import Device, SysParams, Platform
from peewee import Model

@app.route('/api')
def index():
    return make_response(jsonify({'error': error}), 404)

# Register blueprint(s)
app.register_blueprint(devices_module, url_prefix='/api/devices')
