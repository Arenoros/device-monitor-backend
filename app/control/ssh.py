import paramiko 
from collections import namedtuple

#Target = namedtuple('Target', 'ip port user secret')
class Target:
    def __init__(self, ip, port, user, secret):
        self.ip = ip
        self.port = port
        self.user = user
        self.secret = secret

class Executor:
    def __init__(self, target: Target):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=target.ip, username=target.user, password=target.secret, port=target.port)
       # self.sftp = self.client.open_sftp()

    def exec(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        return stdout.read().decode().strip()

    def exec_b(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        return stdout.read()

    def download(self, ):
        #self.sftp.put(localpath, remotepath)
        pass

    def find(self, path, pattern):
        res = []
        for f_path in executor.exec(f'find {path} -name "{pattern}"').split('\n'):
            if not f_path: continue
            res.append(f_path)
        return res

    def close(self):
        self.sftp.close()
        self.client.close()

class LoadInfo:
    def check_cmd(connect):
        commands = ['pidof', 'pkill', 'tar', 'grep', 'ulimit', 'file']
        for cmd in commands:
            test = f'echo -n $({cmd} > /dev/null 2>&1; echo $?)'
            res = connect.exec(test)
            exist = "127" not in res
            print(f'{cmd} : {exist}')

    def find_libs(connect):
        download_list = []

        libso_list = connect.find('/lib', 'libc.so*')

        libstd_list = connect.find('/usr/lib', 'libstdc++.so.*')
        if not libstd_list:
            libstd_list = connect.find('/lib/', 'libstdc++.so.*')

        print(libso_list)
        print(libstd_list)

    def uname(connect):
        machine = connect.exec('uname -m')
        kernel_s = connect.exec('uname -s')
        kernel_r = connect.exec('uname -r')
        os = connect.exec('uname -o')
        print([kernel_s,kernel_r, os, machine])

    def fail_info(connect):
        file_info = executor.exec('file $(which file)')
        print(file_info)

    def all_info(connect):
        LoadInfo.check_cmd(connect)
        LoadInfo.find_libs(connect)
        LoadInfo.uname(connect)
        LoadInfo.fail_info(connect)


linux = Target('10.0.0.213', 2200, 'build', '1')
wirenboard5 = Target('10.0.6.50', 22, 'root', 'wirenboard')
trai915 = Target('10.0.6.41', 22, 'root', 'root')
plc110m2 = Target('10.0.6.13', 22, 'root', '')

executor = Executor(plc110m2)
LoadInfo.all_info(executor)
