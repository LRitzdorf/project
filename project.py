#!/usr/bin/env python

import sys
import argparse

LINUX = 1
MACOS = 2
WINDOWS = 3


def get_os():
    platform = sys.platform
    if platform.startswith('linux') or platform.startswith('cygwin'):
        return LINUX
    elif platform.startswith('darwin'):
        return MACOS
    elif platform.startswith('win32'):
        return WINDOWS
    else:
        print(f"We don't currently support your OS, which we think is {platform}. If you feel it should be supported, "
              "please open an issue (or a PR!) at https://github.com/LRitzdorf/project.")


def parse_config(path):
    platforms = dict()
    templates = False
    try:
        with open(path) as conf:
            for line in conf:
                line = line.strip()
                if line.startswith('#') or line.isspace():
                    continue
                if line.startswith('templates '):
                    templates = line[10:].lstrip()

                line = line.split('$')
                for name in line[0].split():
                    platforms[name.strip()] = [part.strip() for part in line[1:]]
    except FileNotFoundError:
        print(f'Could not find configuration file at {path}. Please ensure it is filled - without a configuration, '
              'Project is likely to be almost useless.')
    except Exception as e:
        print('An error occurred. See traceback for details:')
        raise e
    return platforms, templates


def main(args):
    print('Input received:', args)  # DEBUG

    parser = argparse.ArgumentParser(prog='Project',
                                     description='Set up a new project folder, complete with a variety of template '
                                                 'files, or even a Git/GitHub repo.',
                                     epilog='Feel free to contribute at https://github.com/LRitzdorf/project !')
    parser.add_argument('name', metavar='ProjectName', type=str, nargs='+')

    os = get_os()
    platforms, template_path = parse_config('./project.conf')
    if not template_path:
        template_path = '~/.project/templates/'

    # TODO: Add args from config file to parser

    print('DEVELOPMENT: Ready to run at this point!')  # TODO


if __name__ == '__main__':
    main(sys.argv)
