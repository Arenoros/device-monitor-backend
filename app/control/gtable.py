import re
import os
from app.wrappers import Shell, GoogleApi, TempFile
import nmap

from app.device.types import Controller, State
#from collections import namedtuple

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
        res = []
        test = self.google_api.readTable(self.table, 'A3:K100')
        for row in test['values']:
            if len(row) < 4: continue
            name, ip, auth, protocol = row[:4]
            if 'ssh' in protocol: 
                protocol = 'ssh'
            elif 'telnet' in protocol:
                protocol = 'telnet'
            else:
                continue
            for ip in re.findall(r'(10\.\d+\.\d+\.\d+)', ip):
                login, password = ControllersInfo.split(auth)
                res.append({
                    'name': name, 
                    'ip': ip, 
                    'login': login, 
                    'password': password,
                    'protocol': protocol
                })
        return res

    def __init__(self):
        self.list = {}
    
    # [name, ip, login, pass]
    def load_from_list(self, data):
        for row in data:
            if len(row) < 4: continue
            self.add_controller(*row[:4])

    def update_controller(self, ip, name=None, login=None, password=None, protocol=None):
        cntrl = self.list[ip]
        if name: cntrl.name = name
        if login: cntrl.login = login
        if password: cntrl.password = password
        if protocol: cntrl.protocol = protocol
        return cntrl

    def add_controller(self, name, ip, login, password, protocol):
        if ip in self.list: 
            return self.update_controller(ip, name, login, password, protocol)
        cntrl = Controller(name, ip, login, password, protocol)
        self.list[ip] = cntrl
        return cntrl

    def update_state(self, list_ip):
        res = []
        with TempFile() as tmp:
            for ip in list_ip:
                tmp.write(f'{ip}\n')
            check = self.nm.scan(f'-iL "{tmp.path}"', arguments='-sn -T5')
            for ip in list_ip:
                state = State.UP if ip in check['scan'] else State.DOWN
                cntrl = self.list.get(ip, None)
                if cntrl: cntrl.state = state
                res.append(state)
        return res

    def print(self):
        for cntrl in self.list.values():
            print(cntrl)

