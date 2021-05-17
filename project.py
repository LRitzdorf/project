#!/usr/bin/env python3

from os.path import expanduser
import argparse
# import re
# import shutil


def parse_config(path):
    # TODO: Validate lines before processing. Use re.compile(exp).match(str)
    # Regex: r'^(.+?\s*?)\$(\s*?.+?\s*?)\$(\s*?.*?\s*?)\$((?:\s*?\S+? .+?)?)$'
    names = list()
    platforms = dict()
    templates = False
    err = False
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


def build_parser(names, platforms):
    err = False
    parser = argparse.ArgumentParser(description='''
                                        Sets up a new project folder, complete with a variety of template files, or even
                                        a Git/GitHub repo. All options below are controlled via the config file.''',
                                     epilog='Feel free to contribute at https://github.com/LRitzdorf/project !')
    parser.add_argument('name', metavar='ProjectName', type=str, nargs='?', default='NewProject',
                        help='Name of the project to create (default: %(default)s)')

    # names format is list of "fullname fn"
    # platforms format is dict: "fullname" -> ["file or cmd", "arg names", "specs"]
    for name_set in names:
        name_set = name_set.split()
        try:
            if (args := platforms[name_set[0]][1]) == '':
                # No arguments to be passed
                if len(name_set) == 1:
                    parser.add_argument('-' + name_set[0], action='append_const', const=True)
                else:
                    parser.add_argument('-' + name_set[0], '-' + name_set[1], action='append_const', const=True)
            else:
                # Arguments required
                if len(name_set) == 1:
                    parser.add_argument('-' + name_set[0], action='extend', nargs='*', type=str,
                                        metavar=tuple(args.split()))
                else:
                    parser.add_argument('-' + name_set[0], '-' + name_set[1], action='extend', nargs='*', type=str,
                                        metavar=tuple(args.split()))
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


def main():

    # Read config file, load platforms
    proj_dir = expanduser('~') + '/.project/'
    template_path = proj_dir + 'templates/'
    # TODO: Process specs (at platforms[''][2]) in parse_config()? {'incl': ['git'], 'excl': ['cmd', 'md']}
    names, platforms, template_path, err = parse_config(proj_dir + 'project.conf')
    if err:
        return err

    # Build argument parser
    parser, err = build_parser(names, platforms)

    # DEBUG
    from os import environ
    if 'PYCHARM_HOSTED' in environ:
        print(parser.parse_args(input('project> ').split()))
    else:
        args = parser.parse_args()

    # Continue here...

    return 0


if __name__ == '__main__':
    exit(main())
