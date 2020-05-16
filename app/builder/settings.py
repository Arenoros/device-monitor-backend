#!/usr/bin/env python3

import re
import sys
import os
import os.path
from pathlib import Path
from collections import namedtuple
from typing import List, Dict, Tuple
from app.wrappers import Shell

def regex_map(regex, text, func):
    pos = 0
    res = ''
    for x in re.finditer(regex, text):
        res += text[pos:x.start()]
        pos = x.end()
        res += func(*x.groups())
    res += text[pos:] if not pos == 0 else text
    return res

class Settings:
    
    wrap = ['AR', 'AS', 'RANLIB', 'LD', 'STRIP', 'CC', 'CXX', 'CXXFLAGS','CFLAGS', 'LDFLAGS', 'CMAKE_TOOLCHAIN_FILE']
     # [(r'^/opt/', 'g:')]

    @staticmethod
    def expand_var(vars, name, stack):
        val = vars.get( name, '')
        stack.add(name)
        return regex_map(r'\${?(\w+)}?', val, lambda name: '' if name in stack else Settings.expand_var(vars, name, stack))

    @staticmethod
    def normalize(val):
        return re.sub(r' +', ' ', val).replace('"', '').strip()
        
    @staticmethod
    def read_vars(vars, text):
        for x in re.finditer(r'(\w+)=(.*)', text):
            name, val = x.groups()
            if name in vars:
                vars['__']=val
                val = Settings.expand_var(vars, '__', set())
                del vars['__']
            vars[name] = Settings.normalize(val)

        for x in re.finditer(r'(\w+)\+=(.*)', text):
            name, val = x.groups()
            if name in vars:
                vars[name] += Settings.normalize(val)
            else:
                vars[name] = Settings.normalize(val)

        return vars

    def __load_toolchain_info(self):
        cxxflags = ''
        cflags = ''
        ldflags = ''
        def parse(val: str):
            arr = val.split()
            return (arr[0], ' '.join(arr[1:])) if arr else ('', '')

        for name in self.wrap:
            val = ''
            if name == 'CXX':
                val, cxxflags = parse(self.var('CXX') or self.var('CPP_COMPILER') or self.var('CXX_COMPILER') or self.prefix + 'g++')
            elif name == 'CC':
                val, cflags = parse(self.var('CC') or self.var('C_COMPILER') or self.prefix + 'gcc')
            elif name == 'LD':
                val, ldflags = parse(self.var('LD'))
            else:
                val = self.var(name)
            self.toolchain_vars[name] = val
            self.settings.pop(name, None)

        if cxxflags:
            self.toolchain_vars['CXXFLAGS'] += ' ' + cxxflags
        if cflags:
            self.toolchain_vars['CFLAGS'] += ' ' + cflags
        if ldflags:
            self.toolchain_vars['LDFLAGS'] += ' ' + ldflags 
        for key, value in self.settings.items():
            if 'SYSROOT' in key: 
                self.toolchain_vars['SYSROOT'] = self.var(key)
                break
        self._cc_version = self.__load_cc_version()

    def __load_cc_version1(self) -> str:
        for path in self.path:
            for filename in os.listdir(self.__fix_path(path)):
                if self.cc in filename:
                    match = re.search(rf'{self.cc}-(\d+\.\d+)', filename)
                    if match: return match.group(1)
        return None

    def __load_cc_version(self) -> str:
        for var in ['QNX_HOST', 'QNX_TARGET']:
            if self.var(var):
                self._environ[var] = self.var(var)
        self._environ['PATH'] += ':' + self.var('PATH')
        res, _, _ = Shell.run3(f'{self.cc} --version',self._environ)
        match = re.search(r'\(.*\) (\d+\.\d+)', res)
        if not match:
            match = re.search(r'clang version (\d+\.\d+)', res)
        return match.group(1) if match else self.__load_cc_version1()
    
    def __fix_path(self, path):
        if not path: return ''

        for pattern, repl in self._replace_path.items():
            path = re.sub(pattern, repl, path)
        
        is_absolute = path[0] == '/' or (len(path) > 1 and path[1] == ':')
        if self.cwd and not is_absolute:
            path = f'{self.cwd}/{path}'

        return path

    def __read(self, path):
        source = self.__fix_path(path)
        if not os.path.isfile(source): return ''
        with open(source, 'r', encoding='utf-8', errors='ignore') as f:
            return re.sub(r'(#.*)\n','\n', f.read())

    def __init__(self, 
                    path: str, 
                    replace_path : Dict[str, str] = {}, 
                    env : dict = os.environ.copy(), 
                    platform : str = None,
                    cwd : str = None):
        self.settings={}
        self.path=[]
        self.toolchain_vars = {}
        self._compiler = 'gcc'
        self._cc_version = None
        self.cwd = cwd
        self._settings_sh = path
        self._replace_path = replace_path or {}
        self._environ = env
        self.platform_name = platform
        self.load()

    def __enter__(self):
        #self._environ = os.environ.copy()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        #os.environ.clear()
        #os.environ.update(self._environ)
        pass
        
    def load(self):
        text = regex_map(r'(source|\.) +(.*)\n', self.__read(self._settings_sh), lambda _, source: self.__read(source)+'\n')
        self.settings = self.read_vars({}, text)
        self.path = [x for x in self.var('PATH').split(':') if not x == '']
        self.__load_toolchain_info()
        
    def var(self, name):
        return Settings.expand_var(self.settings, name, set())
   
    @property
    def env(self):
        return self._environ

    @property
    def platform(self):
        Platform = namedtuple('Platform', 'os arch name')
        match=re.search(r'(?P<os>\w+)-(?P<arch>\w+)', self.var('MPLC_PLATFORM'))
        if match is None: return Platform('Linux', 'x86_64', self.platform_name)
        
        os_type = {
            'linux': 'Linux',
            'android': 'Android',
            'qnx': 'Neutrino',
            'unknown': 'Linux'
        }.get(match.group('os'),match.group('os'))

        arch_type = {
            'armv7a' : 'armv7',
            'armv7' : 'armv7hf',
            'armv5te': 'armv5el',
            'elbrus': 'mipsel', #'e2k',
            'mips32': 'mips',
            'x64': 'x86_64',
        }.get(match.group('arch'), match.group('arch'))
        return Platform(os_type, arch_type, self.platform_name)

    #def export_env(self):


    @property
    def cc_version(self) -> str:
        return self._cc_version

    @property
    def build_type(self) -> str:
        if self.var('RELWITHDEBINFO') == '1':
            return 'RelWithDebInfo'
        elif self.var('DEBUG') == '1':
            return 'Debug'
        else:
            return 'Release'

    @property
    def target(self) -> str:
        match = re.search(r'(.*)-', self.prefix)
        return match.group(1) if match else ''

    @property
    def prefix(self) -> str:
        return self.var('CROSS')
        
    @property
    def std(self):
        match=re.search(r'(\w+)\+\+(..)', self.var('STD_CPP'))
        Std = namedtuple('Std', 'libcxx cppstd')
        if match is None:
            return Std('libstdc++', 'None')

        std_type, cppstd = match.groups()
        cppstd = {
            '03': '98',
            '0x': '11'
        }.get(cppstd, cppstd)

        libcxx = 'libstdc++' if cppstd == '98' else 'libstdc++11'
        if std_type == 'gnu':
            cppstd = 'gnu' + cppstd 
        return Std(libcxx,  cppstd)

    @property
    def cmake_toolchain(self) -> str:
        return self.__fix_path(self.toolchain_vars.get('CMAKE_TOOLCHAIN_FILE', ''))
    
    @property
    def sysroot(self) -> str:
        return self.__fix_path(self.toolchain_vars.get('SYSROOT', ''))

    @property
    def ar(self) -> str:
        return self.toolchain_vars.get('AR', self.prefix + 'ar')
    @property
    def ar(self) -> str:
        return self.toolchain_vars.get('AR', self.prefix + 'ar')

    @property
    def as_(self) -> str:
        return self.toolchain_vars.get('AS' or self.prefix + 'as')

    @property
    def ranlib(self) -> str:
        return self.toolchain_vars.get('RANLIB' or self.prefix + 'ranlib')

    @property
    def ld(self) -> str:
        return self.toolchain_vars.get('LD' or self.prefix + 'ld')

    @property
    def strip(self) -> str:
        return self.toolchain_vars.get('STRIP' or self.prefix + 'strip')

    @property
    def cc(self) -> str:
        return self.toolchain_vars.get('CC' or self.prefix + 'gcc')

    @property
    def cxx(self) -> str:
        return self.toolchain_vars.get('CXX' or self.prefix + 'g++')

    @property
    def cflags(self) -> str:
        return self.toolchain_vars.get('CFLAGS' or '')
        
    @property
    def cxxflags(self) -> str:
        return self.toolchain_vars.get('CXXFLAGS' or '')
    @property
    def ldflags(self) -> str:
        return self.toolchain_vars.get('LDFLAGS' or '')

    @property
    def compiler(self) -> str:
        compilers = ['sun-cc', 'apple-clang', 'intel', 'qcc', 'clang', 'gcc']
        for cc in compilers:
            if cc in self.cc:
                return cc
