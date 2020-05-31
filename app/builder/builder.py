import os
import io
import re
import sys
from pathlib import Path
from app.builder.settings import Settings
from app.wrappes import Shell, YamlWrapper

class ConanProfile:
    # settings: Settings = None

    def __init__(self, settings: Settings):
        self.settings = settings
    def __repr__(self):
        return "YamlWrapper()"

    def __str__(self):
        return self.profile()

    def host(self, out: io.StringIO):
        out.write(f'os_build=Linux\n')
        out.write(f'arch_build=x86_64\n')

    def compiler(self, out: io.StringIO):
        tools = self.settings
        out.write(f'compiler={tools.compiler}\n')
        out.write(f'compiler.version={tools.cc_version}\n')
        out.write(f'compiler.libcxx={tools.std.libcxx}\n')
        out.write(f'compiler.cppstd={tools.std.cppstd}\n')

    def target(self, out: io.StringIO):
        tools = self.settings
        out.write(f'arch={tools.platform.arch}\n')
        out.write(f'os={tools.platform.os}\n')
        if tools.platform.os == 'Neutrino':
            out.write(f'os.version=6.5\n')
        elif tools.platform.os == 'WindowsCE':
            out.write(f'os.version=5.0\n')
            out.write(f'os.platform=PAC270\n')
        elif tools.platform.os == 'Android':
            match = re.search(r'-androideabi(\d+)-', tools.cc)
            if match:
                out.write(f'os.api_level={match.group(1)}\n')

    def build_type(self, out: io.StringIO):
        b_type = self.settings.build_type or 'Release'
        out.write(f'build_type={b_type}\n')

    def toolchain_env(self, out: io.StringIO):
        tools = self.settings
        # if tools.platform.os == 'Android':
        #     /android/toolchain.cmake\n')
        # #self.settings.env['CONAN_CMAKE_FIND_ROOT_PATH'] = f'"/ {tools.sysroot}"' ---- Not work
        out.write(f'CONAN_CMAKE_TOOLCHAIN_FILE={tools.cmake_toolchain}\n' if tools.cmake_toolchain else '' )
        out.write(f'CONAN_CMAKE_FIND_ROOT_PATH="{tools.sysroot}"\n' if tools.sysroot else '' ) #--- This too
        out.write(f'PATH={tools.path}\n' if tools.path else '')
        out.write(f'CHOST={tools.target}\n' if tools.target else '')
        out.write(f'AR={tools.ar}\n' if tools.ar else '')
        out.write(f'AS={tools.as_}\n' if tools.as_ else '')
        out.write(f'RANLIB={tools.ranlib}\n' if tools.ranlib else '')
        out.write(f'LD={tools.ld}\n' if tools.ld else '')
        out.write(f'STRIP={tools.strip}\n' if tools.strip else '')
        out.write(f'CC={tools.cc}\n' if tools.cc else '')
        out.write(f'CXX={tools.cxx}\n' if tools.cxx else '')
        out.write(f'CFLAGS={tools.cflags}\n' if tools.cflags else '')
        out.write(f'CXXFLAGS={tools.cxxflags}\n' if tools.cxxflags else '')
        out.write(f'LDFLAGS={tools.ldflags}\n' if tools.ldflags else '')


    def toolchain_opt(self, out: io.StringIO):
        if self.settings.platform.name == 'elbrus':
            out.write(f'openssl:no_async=True\n')
            out.write(f'libpq:with_spinlock=False\n')
        if self.settings.platform.os == 'Neutrino':
            out.write(f'openssl:shared=False\n')

    def settings_section(self, out: io.StringIO()):
        out.write('[settings]\n')
        self.host(out)
        self.target(out)
        self.compiler(out)
        self.build_type(out)

    def env_section(self, out: io.StringIO()):
        out.write('[env]\n')
        self.toolchain_env(out)

    def options_section(self, out: io.StringIO()):
        out.write('[options]\n')
        self.toolchain_opt(out)

    def generate(self, out: io.StringIO()):
        self.env_section(out)
        self.settings_section(out)
        self.options_section(out)

    def profile(self) -> str:
        out = io.StringIO()
        self.generate(out)
        return out.getvalue()

class ConanBuilder:
    conan_settings = f'{Path.home()}/.conan/settings.yml'
    use_profile = ['create', 'install', 'build']
    def __init__(self, settings: Settings, namespace:str = None, shell: Shell = None):
        self.tmp_profile = TempFile()
        self.settings = settings
        self._environ = settings.env
        self.profile = ConanProfile(self.settings)
        self.tmp_profile.write(self.profile.profile())
        self.namespace = namespace
        self.shell = shell or Shell().run
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.tmp_profile.remove()
        pass

    def has_version(self):
        tools = self.settings
        conan_cfg = YamlWrapper(self.conan_settings)
        ver_path = f'compiler.{tools.compiler}.version'
        return conan_cfg.has(ver_path, tools.cc_version)

    def cmd(self, cmd, path):
        append = ''
        if cmd in self.use_profile:
            append += f'--profile {self.tmp_profile.path}'
        return f'conan {cmd} {path} {self.namespace or ""} --build=missing {append}'
    
    def install(self, path):
        return self.shell(self.cmd('install', path), self._environ)

    def create(self, path):
        return self.shell(self.cmd('create', path), self._environ)
    
    def conan(self, argv):
        params = argv.split() if type(argv) is str else argv
        profile = f' --profile {self.tmp_profile.path}' if params[0] in self.use_profile else ''
        return self.shell(f'conan {" ".join(params)} {profile}', self._environ)
