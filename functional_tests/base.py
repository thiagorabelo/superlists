import functools
import inspect
import os
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


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


class ExplicitWaitMixin:  # pylint: disable=too-few-public-methods
    @staticmethod
    def wait_for(func, *args, max_wait=10, step_wait=0.5, **kwargs):
        @wait(max_wait=max_wait, step_wait=step_wait)
        @functools.wraps(func)
        def proxy_dummy(*args_, **kwargs_):
            return func(*args_, **kwargs_)

        return proxy_dummy(*args, **kwargs)


class FunctionalTest(ExplicitWaitMixin, StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.live_server_url = f'http://{staging_server}'

    def tearDown(self):
        self.browser.quit()

    def submit_data_by_post(self, text, id_input='id_new_item'):
        inputbox = self.browser.find_element_by_id(id_input)
        inputbox.clear()
        inputbox.send_keys(text)
        inputbox.send_keys(Keys.ENTER)

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])
