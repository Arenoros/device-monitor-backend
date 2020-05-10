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

    def split(val):
        if not ',' in val: return ['', '']
        first, second = val.split(',')
        return [first.strip(), '' if 'нет' in second else second.strip()]
    def __init__(self, name, ip, auth):
        self.name = name
        self.ip = ip
        self.user, self.password = Controller.split(auth)
        self.staate = State.UNKNOWN

    def __str__(self):
        v = {'name': self.name, 'ip': self.ip, 'user': self.user, 'pass': self.password, 'state': self.staate }
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

    def __init__(self):
        test = self.google_api.readTable(self.table, 'A3:K100')
        self.controllers = {}
        for row in test['values']:
            if len(row) < 4: continue
            name, ip, auth, protocol = row[:4]
            if not 'ssh' in protocol: continue
            for ip in re.findall(r'(10\.\d+\.\d+\.\d+)', ip):
                if ip in self.controllers:
                    print(f'Warn: dublicate {ip} with {[name, auth, protocol]}, prev: {self.controllers[ip]}')
                    continue
                self.controllers[ip] = Controller(name, ip, auth)
        
    def update_state(self):
        with TempFile() as tmp:
            for ip in self.controllers: 
                tmp.write(f'{ip}\n')
            check = self.nm.scan(f'-iL "{tmp.path}"', arguments='-sn -T5')
            for ip, cntrl in self.controllers.items():
                cntrl.staate = State.UP if ip in check['scan'] else State.DOWN

    def print(self):
        for cntrl in self.controllers.values():
            print(cntrl)

controllers = ControllersInfo()
controllers.update_state()
controllers.print()