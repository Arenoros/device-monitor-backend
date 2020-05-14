from enum import Enum

class State(str, Enum):
    UNKNOWN = 'UNKNOWN'
    UP = 'UP'
    DOWN = 'DOWN'

class Controller:
    def __init__(self, name, ip, login, password, protocol, state = State.UNKNOWN):
        self.name = name
        self.ip = ip
        self.login = login
        self.password = password
        self.protocol = protocol
        self.state = state

    def to_dict(self):
        return {
            'name': self.name, 
            'ip': self.ip, 
            'login': self.login, 
            'password': self.password,
            'protocol': self.protocol,
            'state':  self.state == State.UP 
        }
    def from_dict(device):
        return Controller(
            name=device['name'],
            ip=device['ip'],
            login=device['login'],
            password=device.get('password', None),
            protocol=device['protocol'],
            state=device.get('state', State.UNKNOWN)
        )

    def __str__(self):
        return f'{self.to_dict()}'
