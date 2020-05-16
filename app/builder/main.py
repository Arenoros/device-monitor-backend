from builder import ConanBuilder, YamlWrapper, Settings, Shell
import sys
from pathlib import Path
import argparse
import os

conf = YamlWrapper(BUILDER_CONFIG)
root_dir        = conf['settings.root']
replace_path    = conf['settings.replace_path']

def execute(target, args):
    setting_sh = f'{root_dir}/targets/{target}/settings.sh'
    tools = Settings(setting_sh, platform=target, cwd=root_dir, replace_path=replace_path)
    with ConanBuilder(tools) as builder:
        return builder.conan(args)

def install(targets, conanfile_path, pkg_dir):
    failed = []
    successed = []
    for target in targets:
        install_path = f'{pkg_dir}/{target}'
        os.makedirs(f'{install_path}', exist_ok=True)
        if execute(target, f'install {conanfile_path} -if {install_path}'):
            failed.append(target)
        else:
            successed.append(target)
            #execute(target, f'imports -if {install_path} -imf {install_path} {conanfile_path}')

    print(f'Successed: {successed}')
    print(f'Failed: {failed}')

def main():
    name = sys.argv[1]
    setting_sh = f'{root_dir}/targets/{name}/settings.sh'
    tools = Settings(setting_sh, platform=name, cwd=root_dir, replace_path=conf['settings.replace_path'])
    with ConanBuilder(tools) as builder:
        builder.conan(sys.argv[2:])

def targets_list():
    return list(filter(lambda t : not "skip-" in t, os.listdir(f'{root_dir}/targets')))
    #return [ target for target in targets os.listdir(f'{root_dir}/targets') if not "skip-" in target ]

if __name__ == '__main__':
    #main()
    #print(targets_list())
    install(targets_list(), sys.argv[1], f'{Path.home()}/test')

    