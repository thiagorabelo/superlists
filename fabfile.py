# pylint: disable=missing-docstring

import random

from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, cd


REPO_URL = 'https://github.com/thiagorabelo/superlists.git'


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('source', 'virtualenv'):
        run(f'mkdir -p "{site_folder}/{subfolder}"')


def _get_latest_source(source_folder):
    if exists(f'{source_folder}/.git'):
        with cd(source_folder):
            run('git fetch')
    else:
        run(f'git clone {REPO_URL} {source_folder}')

    current_commit = local('git log -n 1 --format=%H', capture=True)

    with cd(source_folder):
        run(f'git reset --hard {current_commit}')


def _update_settings(source_folder, site_name):
    setting_path = f'{source_folder}/superlists/settings.py'
    sed(setting_path, 'DEBUG = True', 'DEBUG = False')
    sed(setting_path, 'ALLOWED_HOSTS =.+$', f'ALLOWED_HOSTS = ["{site_name}"]')
    secret_key_file = f'{source_folder}/superlists/secret_key.py'

    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, f'SECRET_KEY = "{key}"')
        run(f'echo -e "\\n" >> {setting_path}')
        append(setting_path, 'from .secret_key import SECRET_KEY')


def _update_virtualenv(source_folder):
    virtualenv_folder = f'{source_folder}/../virtualenv'
    pip_path = f'{virtualenv_folder}/bin/pip'

    if not exists(pip_path):
        run(f'python3.6 -m venv {virtualenv_folder}')
    run(f'{pip_path} install -q -r {source_folder}/requirements.txt')


def _update_static_files(source_folder):
    with cd(source_folder):
        run('../virtualenv/bin/python manage.py collectstatic --noinput -v 0')


def _update_database(source_folder):
    with cd(source_folder):
        run('../virtualenv/bin/python manage.py migrate --noinput')


def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    source_folder = f'{site_folder}/source'

    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)
