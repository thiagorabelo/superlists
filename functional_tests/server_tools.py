import os

from fabric.api import run, env
# from fabric.context_managers import settings


def _get_manage_dot_py(host):
    return f'~/sites/{host}/virtualenv/bin/python ~/sites/{host}/source/manage.py'


def configure_fabric():
    env.user = os.environ['HOST_USERNAME']
    env.host = env.host_string = os.environ['SSH_STAGING_SERVER']
    env.password = os.environ['HOST_PASSWORD']


def reset_database():
    manage_dot_py = _get_manage_dot_py(env.host)

    # with settings():
    run(f'{manage_dot_py} flush --noinput')


def create_session_on_server(email):
    manage_dot_py = _get_manage_dot_py(env.host)

    # with settings():
    session_key = run(f'{manage_dot_py} create_session {email}')
    return session_key.strip()
