import errno
import os
import shutil
import subprocess
import sys
import yaml


def run(*args, **kwargs):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
    stdout, stderr = proc.communicate()
    return (stdout, proc.returncode)


def get_terrafile_path(path):
    if os.path.isdir(path):
        return os.path.join(path, 'Terrafile')
    else:
        return path


def read_terrafile(path):
    try:
        with open(path) as open_file:
            terrafile = yaml.load(open_file)
        if not terrafile:
            raise ValueError('{} is empty'.format(path)) 
    except IOError as error:
        sys.stderr.write('Error loading Terrafile: {}\n'.format(error.strerror))
        sys.exit(1)
    except ValueError as error:
        sys.stderr.write('Error loading Terrafile: {}\n'.format(error))
        sys.exit(1)
    else:
        return terrafile


def has_git_tag(path, tag):
    tags = set()
    if os.path.isdir(path):
        output, returncode = run('git', 'tag', '--points-at=HEAD', cwd=path)
        if returncode == 0:
            tags.update(output.split())
    return tag in tags


def update_modules(path):
    terrafile_path = get_terrafile_path(path)
    module_path = os.path.dirname(terrafile_path)
    module_path_name = os.path.basename(os.path.abspath(module_path))

    terrafile = read_terrafile(terrafile_path)

    for name, repository_details in sorted(terrafile.items()):
        source = repository_details['source']
        version = repository_details['version']
        target = os.path.join(module_path, name)

        # Skip this module if it has already been checked out.
        if has_git_tag(path=target, tag=version):
            print('Fetched {}/{}'.format(module_path_name, name))
            continue

        print('Fetching {}/{}'.format(module_path_name, name))

        # Delete the old directory and clone it from scratch.
        shutil.rmtree(target, ignore_errors=True)
        output, returncode = run('git', 'clone', '--branch={}'.format(version), source, target)
        if returncode != 0:
            sys.stderr.write(output)
            sys.exit(returncode)
