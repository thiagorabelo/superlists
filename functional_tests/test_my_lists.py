from django.conf import settings

from .management.sessions import create_pre_authenticated_session
from .server_tools import create_session_on_server
from .base import FunctionalTest


class MyListTest(FunctionalTest):

    def create_pre_authenticated_session(self, email):
        if self.staging_server:
            session_key = create_session_on_server(self.staging_server, email)
        else:
            session_key = create_pre_authenticated_session(email)

        # Para definir um cookie, precisamos antes acessar o domínio.
        # As páginas 404 são carregadas mais rapidamente.
        self.browser.get(self.live_server_url + '/404_no_such_url')
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/'
        ))

    def test_logged_in_users_list_are_saved_as_my_list(self):
        email = 'edith@testing.org'
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_out(email)

        # Edith quer ficar logada
        self.create_pre_authenticated_session(email)
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_in(email)
