import re
import os
from app.wrappers import Shell, GoogleApi, TempFile
import nmap
from enum import Enum

#from collections import namedtuple

class State(Enum):
    UNKNOWN = 0
    UP = 1
    DOWN = 2

class Controller:
    def __init__(self, name, ip, login, password, state = State.UNKNOWN):
        self.name = name
        self.ip = ip
        self.login = login
        self.password = password
        self.state = state

    def __str__(self):
        v = {'name': self.name, 'ip': self.ip, 'login': self.login, 'pass': self.password, 'state': self.state }
        return f'{v}'

class ControllersInfo:
    def load_nmap():
        if not 'nmap' in os.environ['PATH']:
            os.environ['PATH']+=f'{os.pathsep}{os.environ["VIRTUAL_ENV"]}/bin/nmap'
        return nmap.PortScanner()

    cred_file = 'app/control/creds.json'
    table = '1s7ZfpAD3SH4Ki0s3BeUzhl5bgoLQt9tHoVbpg4OtQts'
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    nm = load_nmap()
    google_api = GoogleApi(cred_file, scopes)

    def split(val):
        if not ',' in val: return ['', '']
        first, second = val.split(',')
        return [first.strip(), '' if 'нет' in second else second.strip()]

    def load_from_gsheets(self):
        test = self.google_api.readTable(self.table, 'A3:K100')
        for row in test['values']:
            if len(row) < 4: continue
            name, ip, auth, protocol = row[:4]
            if not 'ssh' in protocol: continue
            for ip in re.findall(r'(10\.\d+\.\d+\.\d+)', ip):
                self.add_controller(name, ip, *self.split(auth))

    def __init__(self):
        self.list = {}
    
    # [name, ip, login, pass]
    def load_from_list(self, data):
        for row in data:
            if len(row) < 4: continue
            self.add_controller(*row[:4])

    def update_controller(self, name, ip, login, password):
        cntrl = self.list[ip]
        cntrl.name = name
        cntrl.login = login
        cntrl.password = password
        return cntrl

    def add_controller(self, name, ip, login, password):
        if ip in self.list: 
            return update_controller(ip, name, login, password)
        cntrl = Controller(name, ip, login, password)
        self.list[ip] = cntrl
        return cntrl

    def check_state(self):
        with TempFile() as tmp:
            for ip in self.list: 
                tmp.write(f'{ip}\n')
            check = self.nm.scan(f'-iL "{tmp.path}"', arguments='-sn -T5')
            for ip, cntrl in self.list.items():
                cntrl.state = State.UP if ip in check['scan'] else State.DOWN

    def print(self):
        for cntrl in self.list.values():
            print(cntrl)

