import errno
import os
import shutil
import subprocess
import sys
import yaml
import requests
import re


REGISTRY_BASE_URL = 'https://registry.terraform.io/v1/modules/'

def get_source_from_registry(module_name):
    response = requests.get('{}{}'.format(REGISTRY_BASE_URL, module_name))
    data = response.json()
    if 'errors' not in data.keys():
        return data['source']
    else:
        sys.stderr.write('Error looking up module in Terraform Registry: {}\n'.format(data['errors']))
        sys.exit(1)

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


def is_valid_registry_source(source):
    name_sub_regex = '[0-9A-Za-z](?:[0-9A-Za-z-_]{0,62}[0-9A-Za-z])?'
    provider_sub_regex = '[0-9a-z]{1,64}'
    registry_regex = re.compile('^({})\\/({})\\/({})(?:\\/\\/(.*))?$'.format(name_sub_regex, name_sub_regex, provider_sub_regex))
    if registry_regex.match(source):
        return True
    else:
        return False


def update_modules(path):
    terrafile_path = get_terrafile_path(path)
    module_path = os.path.dirname(terrafile_path)
    module_path_name = os.path.basename(os.path.abspath(module_path))

    terrafile = read_terrafile(terrafile_path)

    for name, repository_details in sorted(terrafile.items()):
        target = os.path.join(module_path, name)
        raw_source = repository_details['source']
        if is_valid_registry_source(raw_source):
            source = get_source_from_registry(raw_source)
        elif os.path.isdir(raw_source):
            source = os.path.abspath(raw_source)
            shutil.rmtree(target, ignore_errors=True)
            print('Fetching {}/{}'.format(module_path_name, name))
            shutil.copytree(source, target)
            continue
        else:
            source = raw_source
        version = repository_details['version']

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
