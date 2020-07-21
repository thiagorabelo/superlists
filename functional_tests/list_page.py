import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from .base import wait, FunctionalTest


class ListPage:

    def __init__(self, test:FunctionalTest):
        self.test = test

    def _submit_data(self, text, inputbox):
        inputbox.clear()
        time.sleep(0.1)
        inputbox.send_keys(text)
        time.sleep(0.2)
        inputbox.send_keys(Keys.ENTER)

    @property
    def browser(self) -> webdriver.Firefox:
        return self.test.browser

    def get_table_rows(self, css_selector='#id_list_table tr'):
        return self.browser.find_elements_by_css_selector(css_selector)

    @wait(max_wait=5)
    def wait_for_row_in_list_table(self, item_text, item_number):
        expected_row_text = f'{item_number}: {item_text}'
        rows = self.get_table_rows()
        self.test.assertIn(expected_row_text, [row.text for row in rows])

    def get_item_input_box(self, id_input='id_text'):
        return self.browser.find_element_by_id(id_input)

    def submit_data(self, text, id_input='id_text'):
        inputbox = self.get_item_input_box(id_input)
        self._submit_data(text, inputbox)

    def add_list_item(self, item_text, css_selector='#id_list_table tr'):
        new_item_no = len(self.get_table_rows(css_selector)) + 1
        self.submit_data(item_text)
        self.wait_for_row_in_list_table(item_text, new_item_no)
        return self

    def get_share_box(self, css_selector='input[name="sharee"]'):
        return self.browser.find_element_by_css_selector(css_selector)

    def get_shared_with_list(self, css_selector='.list-sharee'):
        return self.browser.find_elements_by_css_selector(css_selector)

    def share_list_with(self, email):
        sharebox = self.get_share_box()
        self._submit_data(email, sharebox)
        self.test.until(max_wait=5).wait(
            lambda: self.test.assertIn(
                email,
                [item.text for item in self.get_shared_with_list()]
            )
        )

    def get_list_owner(self):
        return self.browser.find_element_by_id('id_list_owner').text
