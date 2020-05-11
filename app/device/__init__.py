# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
# Import the database object from the main app module
from app import db
from app.device.model import Device
import json
from app.control.gtable import Controller, State, ControllersInfo
from peewee import IntegrityError
# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_devices = Blueprint('devices', __name__)
controllers = ControllersInfo()
by_id = {}
@mod_devices.route('/', methods=['GET'])
def index():
    res = []
    if not by_id:
        for device in Device.select():
            cntrl = controllers.add_controller(device.name, device.ip, device.login, device.password)
            by_id[device.id] = cntrl
        controllers.check_state()
    for id, cntrl in by_id.items():
        res.append({
            'id': id,
            'name': cntrl.name, 
            'host': cntrl.ip, 
            'login': cntrl.login, 
            'password': cntrl.password, 
            'state':  cntrl.state == State.UP 
        })
    return json.dumps(res)

@mod_devices.route('/', methods=['POST'])
def create():
    form = request.args
    with db.atomic():
        device = Device.create(name=form['name'], ip=form['ip'], login=form['login'], password=form['password'], platform_id=form['platform_id'])
        return json.dumps({'code': 0, 'id': device.id}) if device.save() else json.dumps({'code': 1})

# Set the route and accepted methods
@mod_devices.route('/import', methods=['POST'])
def load_from_gtables():
    controllers.load_from_gsheets()
    with db.atomic():
        for x in controllers.list.values():
            device = Device.insert(
                    name=x.name, 
                    ip=x.ip, 
                    login=x.login, 
                    password=x.password, 
                    platform_id=1
                )
            try:
                device.on_conflict_replace().execute()
            except IntegrityError as err:
                return json.dumps({'code': 1, 'err': err.message})
    return json.dumps({'code': 0})
    

# Set the route and accepted methods
@mod_devices.route('/<id>', methods=['GET'])
def read(id):
    return f"<h1>{id}</h1>"

# Set the route and accepted methods
@mod_devices.route('/update_state', methods=['GET'])
def update_state(id):
    controllers.check_state()
    return f"<h1>{id}</h1>"
