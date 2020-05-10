import gspread
import pprint
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
import apiclient.discovery
from collections import namedtuple
import re
import os
from shell import Shell

TmpInfo = namedtuple('TmpInfo', "name ip auth protocol")
cred_file='app/control/creds.json'
tables = ['1s7ZfpAD3SH4Ki0s3BeUzhl5bgoLQt9tHoVbpg4OtQts']
scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

class GoogleApi:
    def __init__(self, cred_file, scopes):
        self.cred = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scopes)
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scopes)
        httpAuth = creds.authorize(httplib2.Http())
        service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)
        self.service = responce = service.spreadsheets().values()

    def readTable(self, table, range, dimension = 'ROWS'):
        return self.service.get(
            spreadsheetId = table,
            range=range,
            majorDimension=dimension
        ).execute()

# googleT = GoogleApi(cred_file, scopes)
# test = googleT.readTable(tables[0], 'A3:K100')

TmpInfos = [TmpInfo(name='WinPAC 8000', ip='10.0.6.85', auth='sa, 1234', protocol='ftp/telnet'),
 TmpInfo(name='WP9421-CE7', ip='10.0.6.162', auth='sa, 1234', protocol='ftp/telnet'),
 TmpInfo(name='XP', ip='10.0.6.171', auth='Administrator, нет', protocol=''),
 TmpInfo(name='LP', ip='10.0.6.87', auth='root, root', protocol=''),
 TmpInfo(name='ICP CON ET 7002 - модуль', ip='10.0.6.9 (192.168.71.9)', auth='Admin, Admin', protocol=''),
 TmpInfo(name='ADAM 3600', ip='10.0.6.226 (порт 8043)', auth='root, нет', protocol=''),
 TmpInfo(name='ADAM 3600', ip='10.0.6.229', auth='root, нет', protocol=''),
 TmpInfo(name='BTune (S/N 2030304)', ip='10.0.6.227', auth='root, 12345', protocol='ssh/SCP'),
 TmpInfo(name='BTune', ip='10.0.6.228', auth='root, 12345', protocol=''),
 TmpInfo(name='ПЛК 110-30', ip='10.0.6.11', auth='root, нет', protocol='scp/ssh'),
 TmpInfo(name='ПЛК 110-60', ip='10.0.6.31', auth='root, нет', protocol='scp/ssh'),
 TmpInfo(name='ПЛК 110-30 (логотип) 10 кл', ip='10.0.6.12', auth='root, нет', protocol='scp/ssh'),
 TmpInfo(name='ПЛК 110-60 (логотип) 3 клиента', ip='10.0.6.32', auth='root, нет', protocol='scp/ssh'),
 TmpInfo(name='ПЛК 110-60 (старый)', ip='10.0.6.220', auth='root, mplc', protocol='scp/ssh'),
 TmpInfo(name='ПЛК 110-30 (самый новый) 10 кл', ip='10.0.6.15', auth='root, нет', protocol='scp/ssh'),
 TmpInfo(name='ПЛК 110 (выставка ПИТЕР)', ip='10.0.6.10', auth='', protocol='scp/ssh'),
 TmpInfo(name='ПЛК110-30', ip='10.0.6.13', auth='root, нет', protocol=''),
 TmpInfo(name='МК210-302 (модуль DI/DO)', ip='10.0.6.8', auth='', protocol=''),
 TmpInfo(name='МУ210-401 (модуль DO)', ip='10.0.6.7', auth='', protocol=''),
 TmpInfo(name='TREI 915', ip='10.0.6.41, 10.0.6.42', auth='root, root', protocol='ftp/telnet'),
 TmpInfo(name='TREI902', ip='10.0.6.46', auth='root,root', protocol='sftp/ssh,telnet'),
 TmpInfo(name='TREI903', ip='10.0.6.44, 10.0.6.45', auth='root, root', protocol='ftp/telnet'),
 TmpInfo(name='МК3000', ip='10.0.6.205', auth='root, p@ssw0rd1234', protocol=''),
 TmpInfo(name='МК-150, Fastwel', ip='10.0.6.36:22', auth='insat, 123', protocol='sftp/ssh'),
 TmpInfo(name='Regul R500 (старый)', ip='10.0.6.230', auth='root, IeSuxE7Srt', protocol='sftp/ssh'),
 TmpInfo(name='Regul R500 (новый)', ip='10.0.6.231', auth='root, IeSuxE7Srt', protocol='sftp/ssh'),
 TmpInfo(name='Regul R200', ip='10.0.6.232', auth='', protocol=''),
 TmpInfo(name='Regul R400', ip='10.0.6.233', auth='', protocol=''),
 TmpInfo(name='Wiren Board 5', ip='10.0.6.50', auth='root, wirenboard', protocol='ssh/http'),
 TmpInfo(name='Wiren Board 5 (A5PEDTCZ 3G)', ip='10.0.6.53', auth='root, wirenboard', protocol='ssh/http'),
 TmpInfo(name='Wiren Board 6', ip='10.0.6.54', auth='root, wirenboard', protocol=''),
 TmpInfo(name='Moxa UC-8100', ip='10.0.6.222', auth='moxa, moxa', protocol=''),
 TmpInfo(name='Moxa UC-8100 Me', ip='10.0.6.223', auth='moxa, moxa', protocol=''),
 TmpInfo(name='Байкал (Акситех)', ip='10.0.6.117', auth='root, acsitech', protocol='sftp/ssh'),
 TmpInfo(name='Торнадо', ip='10.0.6.106', auth='', protocol=''),
 TmpInfo(name='Торнадо', ip='10.0.6.107', auth='', protocol=''),
 TmpInfo(name='MIRage-NAI Торнадо', ip='10.0.6.108', auth='', protocol=''),
 TmpInfo(name='MIRage-NDI Торнадо', ip='10.0.6.112', auth='', protocol=''),
 TmpInfo(name='MIRage-NAO Торнадо', ip='10.0.6.109', auth='', protocol=''),
 TmpInfo(name='MIRage-NDO Торнадо', ip='10.0.6.110', auth='', protocol=''),
 TmpInfo(name='ASTRALINUX Смоленск 1.6 (Виртуалка)', ip='10.0.6.208', auth='insat, 12345678', protocol=''),
 TmpInfo(name='ASTRALINUX Смоленск 1.5 (Виртуалка)', ip='', auth='', protocol=''),
 TmpInfo(name='ASTRALINUX Орел 2.6 (Виртуалка)', ip='', auth='', protocol=''),
 TmpInfo(name='Ubuntu X64 KINGDY (стенд)', ip='10.0.6.207', auth='insat, insat', protocol='sftp/ssh'),
 TmpInfo(name='Тестовый образец', ip='10.0.6.206', auth='user, 111111', protocol='scp/ssh'),
 TmpInfo(name='IRIS', ip='10.0.6.71', auth='root, root', protocol=''),
 TmpInfo(name='raspberry', ip='10.0.6.109', auth='pi, raspberry', protocol=''),
 TmpInfo(name='RDP сервер 12ой комнаты 2 (Пока не работает)', ip='10.0.0.107', auth='InSat-test, insat', protocol='rdp'),
 TmpInfo(name='ОСАТЕК ЧГП', ip='10.0.6.223', auth='root, 123', protocol='sftp/ssh'),
 TmpInfo(name='Raspberry p1', ip='', auth='pi, raspberry', protocol='sftp/ssh'),
 TmpInfo(name='BeagleBoard', ip='10.0.6.121', auth='debian, temppwd', protocol='sftp/ssh'),
 TmpInfo(name='tion-pro28', ip='10.0.6.221', auth='root, нет', protocol='sftp/ssh')]

class Controller:
    def split(val):
        if not ',' in val: return ['', '']
        first, second = val.split(',')
        return [first.strip(), '' if 'нет' in second else second.strip()]
    def __init__(self, name, ip, auth):
        self.name = name
        self.ip = ip
        self.user, self.password = Controller.split(auth)

    def __str__(self):
        v = {'name': self.name, 'ip': self.ip, 'user': self.user, 'pass': self.password }
        return f'{v}'

def ping(host):
    return 0 == Shell.simple(f'ping -n 1 {host}')

def _getControllers():
    res = []
    for x in TmpInfos:
        if not 'ssh' in x.protocol: continue
        for ip in re.findall(r'(10\.\d+\.\d+\.\d+)', x.ip):
            if not ping(ip): continue
            res.append(Controller(x.name, ip, x.auth))
    return res

# for x in getControllers():
#     print(f'{x},')

getControllers():
    return [{'name': 'BTune (S/N 2030304)', 'ip': '10.0.6.227', 'user': 'root', 'pass': '12345'},
        {'name': 'ПЛК 110-30', 'ip': '10.0.6.11', 'user': 'root', 'pass': ''},
        {'name': 'ПЛК 110-60', 'ip': '10.0.6.31', 'user': 'root', 'pass': ''},
        {'name': 'ПЛК 110-30 (логотип) 10 кл', 'ip': '10.0.6.12', 'user': 'root', 'pass': ''},
        {'name': 'ПЛК 110-60 (логотип) 3 клиента', 'ip': '10.0.6.32', 'user': 'root', 'pass': ''},
        {'name': 'ПЛК 110-60 (старый)', 'ip': '10.0.6.220', 'user': 'root', 'pass': 'mplc'},
        {'name': 'ПЛК 110-30 (самый новый) 10 кл', 'ip': '10.0.6.15', 'user': 'root', 'pass': ''},
        {'name': 'ПЛК 110 (выставка ПИТЕР)', 'ip': '10.0.6.10', 'user': '', 'pass': ''},
        {'name': 'TREI902', 'ip': '10.0.6.46', 'user': 'root', 'pass': 'root'},
        {'name': 'МК-150, Fastwel', 'ip': '10.0.6.36', 'user': 'insat', 'pass': '123'},
        {'name': 'Regul R500 (старый)', 'ip': '10.0.6.230', 'user': 'root', 'pass': 'IeSuxE7Srt'},
        {'name': 'Regul R500 (новый)', 'ip': '10.0.6.231', 'user': 'root', 'pass': 'IeSuxE7Srt'},
        {'name': 'Wiren Board 5', 'ip': '10.0.6.50', 'user': 'root', 'pass': 'wirenboard'},
        {'name': 'Wiren Board 5 (A5PEDTCZ 3G)', 'ip': '10.0.6.53', 'user': 'root', 'pass': 'wirenboard'},
        {'name': 'Байкал (Акситех)', 'ip': '10.0.6.117', 'user': 'root', 'pass': 'acsitech'},
        {'name': 'Ubuntu X64 KINGDY (стенд)', 'ip': '10.0.6.207', 'user': 'insat', 'pass': 'insat'},
        {'name': 'Тестовый образец', 'ip': '10.0.6.206', 'user': 'user', 'pass': '111111'},
        {'name': 'ОСАТЕК ЧГП', 'ip': '10.0.6.223', 'user': 'root', 'pass': '123'},
        {'name': 'BeagleBoard', 'ip': '10.0.6.121', 'user': 'debian', 'pass': 'temppwd'},
        {'name': 'tion-pro28', 'ip': '10.0.6.221', 'user': 'root', 'pass': ''}]