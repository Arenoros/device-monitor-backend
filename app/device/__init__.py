# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, jsonify, abort, make_response

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
    controllers.update_state(controllers.list.keys())

@mod_devices.route('', methods=['GET'])
def index():
    res = {}
    if not by_id: load_from_db()
    return jsonify({'data': [[id, ctrl.to_dict()] for id, ctrl in by_id.items()], 'code': 0})

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
    return id

@mod_devices.route('', methods=['POST'])
def create():
    form = request.get_json()
    print(form)
    id = None
    with db.atomic():
        try:
            id = insert(form)
        except Exception as err:
            return jsonify({'code': 1, 'err': err})
    return jsonify({'data': {'id': id}, 'code': 0})

# Set the route and accepted methods
@mod_devices.route('/import', methods=['POST'])
def load_from_gtables():
    data = controllers.load_from_gsheets()
    with db.atomic():
        for controller in data:
            try:
                insert(controller)
            except Exception as err:
                return jsonify({'code': 1, 'err': err})
    return jsonify({'data': [[id, ctrl.to_dict()] for id, ctrl in by_id.items()], 'code': 0})
    
# Set the route and accepted methods
@mod_devices.route('/update_state', methods=['POST'])
def update_state():
    if not request.json: abort(403)
    list_ip = request.get_json()
    res = controllers.update_state(list_ip)
    return jsonify({'data': res, 'code': 0})

from app.control.ssh import Executor, LoadInfo

# Set the route and accepted methods
@mod_devices.route('/<int:id>', methods=['GET'])
def read(id):
    cntrl = by_id.get(id, None)
    if not cntrl: 
        device = Device.get(Device.id==id)
        if not device: return make_response(jsonify({'error': 'not found'}), 404)
        cntrl = controllers.add_controller(
            device.name, 
            device.ip, 
            device.login,
            device.password, 
            device.protocol)
        by_id[device.id] = cntrl
    controllers.update_state([cntrl.ip])
    if cntrl.state != State.UP:
        return make_response(jsonify({'error': 'controller is down'}), 200)
    exec = Executor(cntrl)
    data = LoadInfo.all_info(exec)
    return jsonify(data)
