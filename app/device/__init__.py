# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
# Import the database object from the main app module
from app import db
from app.device.model import Device
import json

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_devices = Blueprint('devices', __name__, url_prefix='/devices')

@mod_devices.route('/', methods=['GET'])
def index():
    resp = {'fields': ['id','name', 'ip', 'platform_id'], 'data': []}
    data = resp['data']
    for device in Device.select():
        row = [device.id, device.name, device.ip, device.platform_id]
        data.append(row)
    return json.dumps(resp)

@mod_devices.route('/', methods=['POST'])
def create():
    form = request.args
    with db.atomic():
        device = db.Device.create(name=form['name'], ip=form['ip'], login=form['login'], password=form['password'], platform_id=form['platform_id'])
        return json.dumps({'code': 0, 'id': device.id}) if device.save() else json.dumps({'code': 1})


# Set the route and accepted methods
@mod_devices.route('/<id>', methods=['GET'])
def read(id):
    return f"<h1>{id}</h1>"
