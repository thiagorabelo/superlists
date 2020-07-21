# pylint: disable=too-few-public-methods

import functools
import inspect
import os
import time
import typing

from datetime import datetime
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

from . import server_tools
from .management.sessions import create_pre_authenticated_session
from .server_tools import create_session_on_server


def wait(func=None, max_wait=10, step_wait=0.5):

    def decorator(decored_func):
        @functools.wraps(decored_func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            time.sleep(step_wait)

            while True:
                try:
                    return decored_func(*args, **kwargs)
                except (AssertionError, WebDriverException) as ex:
                    if time.time() - start_time > max_wait:
                        raise ex
                    time.sleep(step_wait)
        return wrapper

    if inspect.isfunction(func):
        return decorator(func)

    return decorator


class AdditionalAssertionsMixin:

    def assertEmpty(self, obj):  # pylint: disable=invalid-name
        if not isinstance(obj, typing.Iterable):
            raise AssertionError(f"{obj} is not an Iterable")
        try:
            self.assertFalse(obj)
        except AssertionError as ex:
            raise AssertionError(f"{obj} is not empty") from ex

    def assertNotEmpty(self, obj):  # pylint: disable=invalid-name
        if not isinstance(obj, typing.Iterable):
            raise AssertionError(f"{obj} is not an Iterable")

        try:
            self.assertTrue(obj)
        except AssertionError as ex:
            raise AssertionError(f"{obj} is empty") from ex


SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'screendumps'
)


class OnTestFailureTakeScreenshotAndDumpHTMLMixin:

    def tearDown(self):  # pylint: disable=invalid-name
        if self._test_has_failed():
            os.makedirs(SCREEN_DUMP_LOCATION, exist_ok=True)

            for idx, handle in enumerate(self.browser.window_handles):
                self._windowid = idx
                self.browser.switch_to_window(handle)
                self.take_screenshot()
                self.dump_html()
        super().tearDown()

    def _test_has_failed(self):
        return any(error for (method, error) in self._outcome.errors)

    def take_screenshot(self):
        filename = f'{self._get_filename()}.png'
        print(f'>>> screenshotting to {filename}')
        self.browser.get_screenshot_as_file(filename)

    def dump_html(self):
        filename = f'{self._get_filename()}.html'
        print(f'>>> dumping page HTML to {filename}')
        with open(filename, 'wt') as html_file:
            html_file.write(self.browser.page_source)

    def _get_filename(self):
        timestamp = datetime.now().strftime('%Y-%m-%dT%H.%M.%S')
        return "{folder}/{classname}.{method}-window{windowid}-{timestamp}".format(
            folder=SCREEN_DUMP_LOCATION,
            classname=self.__class__.__name__,
            method=self._testMethodName,
            windowid=self._windowid,
            timestamp=timestamp,
        )


# TODO: Estudar o "headless" dos navegadores e substituir o QUnit por testes modernos no frontend.
#         - `lists/static/testes/`.
#       https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Headless_mode#Selenium_in_Python
class FunctionalTest(OnTestFailureTakeScreenshotAndDumpHTMLMixin,  # pylint: disable=too-many-ancestors
                     AdditionalAssertionsMixin,
                     StaticLiveServerTestCase):

    def setUp(self):
        self.browser = self.get_browser()

        self.staging_server = os.environ.get('STAGING_SERVER')
        if self.staging_server:
            self.live_server_url = f'http://{self.staging_server}'
            server_tools.configure_fabric()

    def tearDown(self):
        # Chama a funcionalidade que tira screenshots e faz dump do html
        # em casos de falhas nos testes.
        super().tearDown()
        self.browser.quit()

    def get_browser(self) -> webdriver.Firefox:
        """
        Retorna um browser, passando o parâmetro `--headless` (sem interface
        gráfica) caso a variável de ambiente `USER_HEADLESS_BROWSER` seja
        definida. Do contrário, um navegador com interface gráfica será retornado.
        """
        if os.environ.get('USER_HEADLESS_BROWSER', None):
            options = Options()
            options.add_argument('--headless')
            return webdriver.Firefox(options=options)
        return webdriver.Firefox()

    def get_item_input_box(self, id_input='id_text'):
        return self.browser.find_element_by_id(id_input)

    def submit_data_by_post(self, text, id_input='id_text'):
        inputbox = self.get_item_input_box(id_input)
        inputbox.clear()
        time.sleep(0.1)
        inputbox.send_keys(text)
        time.sleep(0.2)
        inputbox.send_keys(Keys.ENTER)

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def until(self, max_wait=10, step_wait=0.5):
        class Wait:
            @staticmethod
            def wait(func, *args, **kwargs):
                @wait(max_wait=max_wait, step_wait=step_wait)
                @functools.wraps(func)
                def dummy(*args_, **kwargs_):
                    return func(*args_, **kwargs_)
                return dummy(*args, **kwargs)

        return Wait()

    def add_list_item(self, item_text, css_selector='#id_list_table tr'):
        num_rows = len(self.browser.find_elements_by_css_selector(css_selector))
        self.submit_data_by_post(item_text)
        item_number = num_rows + 1
        self.wait_for_row_in_list_table(f'{item_number}: {item_text}')

    def wait_for_row_in_list_table(self, row_text):
        self.until(max_wait=5).wait(self.check_for_row_in_list_table, row_text)

    @wait(max_wait=5)
    def wait_to_be_logged_in(self, email):
        self.browser.find_element_by_link_text('Log out')
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(email, navbar.text)

    @wait(max_wait=5)
    def wait_to_be_logged_out(self, email):
        self.browser.find_element_by_name('email')
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertNotIn(email, navbar.text)

    def create_pre_authenticated_session(self, email):
        if self.staging_server:
            session_key = create_session_on_server(email)
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