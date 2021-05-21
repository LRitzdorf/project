#!/usr/bin/env python3

import typing
from os.path import expanduser
import argparse
# import re
# import shutil


class ExtendWithDefaultAction(argparse.Action):
    """
    Custom Action class to implement extension of a list, using a default value if none is provided explicitly (i.e. the
    flag in question is use on its own). Using this class, all unique flag parameters are recorded - either with the
    parameter as provided on the command line, or with the default value if no command line value was given.
    """
    def __init__(self, option_strings, dest, default_extend=None, nargs=None, const=None, default=None, type=None,
                 choices=None, required=False, help=None, metavar=None):
        self.default_extend = default_extend
        super().__init__(option_strings=option_strings, dest=dest, nargs=nargs, const=const, default=default, type=type,
                         choices=choices, required=required, help=help, metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        if items is None:
            items = []
        elif type(items) == list:
            items = items[:]
        else:
            from copy import copy
            items = copy(items)
        if not values:
            items.extend([''])
        else:
            items.extend(values)
        setattr(namespace, self.dest, items)


def parse_config(path: str) -> tuple[list[str], dict[str, list[str]], str, int]:
    # TODO: Validate lines before processing. Use re.compile(exp).match(str)
    # Regex: r'^(.+?\s*?)\$(\s*?.+?\s*?)\$(\s*?.*?\s*?)\$((?:\s*?\S+? .+?)?)$'
    names = list()
    platforms = dict()
    templates = ''
    err = 0
    # regex setup
    try:
        with open(path) as conf:
            for line in conf:
                line = line.strip()
                # Add "or not regex.match(line)" below
                if line.startswith('#') or line == '':
                    continue
                if line.startswith('templates '):
                    templates = line[10:].lstrip()
                    continue

                # Use regex to process instead?
                line = line.split('$')
                names.append(line[0].rstrip())
                platforms[line[0].split()[0]] = [part.strip() for part in line[1:]]
    except FileNotFoundError:
        err = 3
        print(f'Could not find configuration file at {path}. Please ensure it is filled - without a configuration, '
              'Project is likely to be almost useless.')
    except Exception as e:
        err = 1
        print('An error occurred while loading the configuration file. See traceback for details:\n', e.args, sep='')
    return names, platforms, templates, err


def build_parser(names: list[str], platforms: dict[str, list[str]]) -> tuple[argparse.ArgumentParser, int]:
    err = 0
    parser = argparse.ArgumentParser(description='''
                                        Sets up a new project folder, complete with a variety of template files, or even
                                        a Git/GitHub repo. All options below are controlled via the config file.''',
                                     epilog='Feel free to contribute at https://github.com/LRitzdorf/project !')
    parser.add_argument('ProjectName', type=str, nargs='?', default='NewProject',
                        help='Name of the project to create (default: %(default)s)')

    # names format is list of "fullname fn"
    # platforms format is dict: "fullname" -> ["file or cmd", "arg names", "incl"]
    for name in names:
        name_list = name.split()
        try:
            if (args := platforms[name_list[0]][1]) == '':
                # No arguments to be passed
                if len(name_list) == 1:
                    parser.add_argument('-' + name_list[0], action='store_true')
                else:
                    parser.add_argument('-' + name_list[0], '-' + name_list[1], action='store_true')
            else:
                # Arguments possible
                nargs = '+' if '{' in platforms[name_list[0]][0] else '*'
                if len(meta := tuple(args.split())) < 2 and nargs == '+':
                    meta = meta + (f'more {meta[0]}s',)
                if len(name_list) == 1:
                    parser.add_argument('-' + name_list[0],
                                        action=ExtendWithDefaultAction, default_extend='',
                                        nargs=nargs, type=str, metavar=meta)
                else:
                    parser.add_argument('-' + name_list[0], '-' + name_list[1],
                                        action=ExtendWithDefaultAction, default_extend='',
                                        nargs=nargs, type=str, metavar=meta)
            # TODO
            # >>> p.parse_args(['-foo', 'example', '-foo', 'again', '-f'])
            # Namespace(foo=['example', 'again', None])
            # vars(result)['foo'] -> ['example', 'again', None]
        except argparse.ArgumentError as e:
            err = 4
            print(f'Error while loading configured platforms:\n"{e.message}".\nThis usually occurs when you configure '
                  'two platforms with the same name (shortnames included). Please fix this in your configuration file. '
                  'The problematic name should be indicated in the above error message.')
            break
    return parser, err


def process_platforms(args: dict[str, typing.Any], platforms: dict[str, list[str]])\
        -> tuple[dict[str, typing.Any], int]:
    err = 0
    requested_platforms = set()
    for platform, value in args.items():
        if value is not None:
            requested_platforms.add(platform)
    necessary_platforms = requested_platforms.copy()
    for platform in requested_platforms:
        if (value := platforms.get(platform)) and value[2] in necessary_platforms:
            necessary_platforms.remove(value[2])
    args = {key: value for key, value in args.items() if key in necessary_platforms}
    return args, err


def create_templates(args, platforms, template_path) -> int:
    err = 0
    # Be sure to notify user of progress if error occurs
    print('We are the knights who say NI!\n(It means "Not Implemented")')
    for platform, value in args.items():
        # if value is None:
        #     pass
        # else:
        print(platform, value, sep='\t')  # Replace with real processing
    return err


def main():

    # Read config file, load platforms
    proj_dir = expanduser('~') + '/.project/'
    names, platforms, template_path, err = parse_config(proj_dir + 'project.cfg')
    if err:
        return err
    if template_path == '':
        template_path = proj_dir + 'templates/'

    # Build argument parser
    parser, err = build_parser(names, platforms)
    if err:
        return err

    # Process command line arguments
    args = vars(parser.parse_args())

    # Process requested platforms
    args, err = process_platforms(args, platforms)

    # Create templates for each platform listed in args
    err = create_templates(args, platforms, template_path)
    if err:
        return err

    return 0


if __name__ == '__main__':
    exit(main())
