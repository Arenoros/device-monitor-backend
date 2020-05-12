# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from app.device.model import Device
from app import db
import json
from app.control.gtable import Controller, State, ControllersInfo
from peewee import IntegrityError
# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_devices = Blueprint('devices', __name__)
controllers = ControllersInfo()
by_id = {}

def load_from_db():
    for device in Device.select():
        cntrl = controllers.add_controller(
            device.name, 
            device.ip, 
            device.login,
            device.password, 
            device.protocol)
        by_id[device.id] = cntrl
    controllers.check_state()

@mod_devices.route('/', methods=['GET'])
def index():
    res = {}
    if not by_id: load_from_db()
    return json.dumps([[id, ctrl.to_dict()] for id, ctrl in by_id.items()]) #json.dumps({id: cntrl.to_dict() for id, ctrl in by_id.items()})

def insert(device):
    id = Device.insert(
            name=device['name'],
            ip=device['ip'],
            login=device['login'],
            password=device['password'],
            protocol=device['protocol'],
            platform_id=device.get('platform_id', None)
        ).on_conflict_replace().execute()
    by_id[id] = Controller.from_dict(device)

@mod_devices.route('/', methods=['POST'])
def create():
    form = request.args
    id = None
    with db.atomic():
        try:
            insert(form)
        except Exception as err:
            return json.dumps({'code': 1, 'err': err.message})
    return json.dumps({'code': 0, 'id': id})

# Set the route and accepted methods
@mod_devices.route('/import', methods=['POST'])
def load_from_gtables():
    data = controllers.load_from_gsheets()
    with db.atomic():
        for controller in data:
            try:
                insert(controller)
            except Exception as err:
                return json.dumps({'code': 1, 'err': err})
    return json.dumps([[id, ctrl.to_dict()] for id, ctrl in by_id.items()])
    
# Set the route and accepted methods
@mod_devices.route('/update_state', methods=['GET'])
def update_state():
    controllers.check_state()
    return json.dumps([ctrl.state == State.UP for ctrl in by_id.values()]  )

# Set the route and accepted methods
@mod_devices.route('/<id>', methods=['GET'])
def read(id):
    return f"<h1>{id}</h1>"

