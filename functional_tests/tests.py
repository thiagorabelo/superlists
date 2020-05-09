#!/usr/bin/env python

import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from . import base


class NewVisitor(StaticLiveServerTestCase, base.ExplicitWaitMixin):

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

    def test_can_start_a_list_for_one_user(self):  # pylint: disable=C0103
        self.browser.get(self.live_server_url)

        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(inputbox.get_attribute('placeholder'),
                         'Enter a to-do item')

        input_text_1 = 'Compre penas de pavão'
        self.submit_data_by_post(input_text_1)
        self.wait_for(self.check_for_row_in_list_table, f'1: {input_text_1}', max_wait=2)

        input_text_2 = 'Usar penas de pavão para fazer um fly'
        self.submit_data_by_post(input_text_2)
        self.wait_for(self.check_for_row_in_list_table, f'1: {input_text_1}', max_wait=2)
        self.wait_for(self.check_for_row_in_list_table, f'2: {input_text_2}', max_wait=2)

        # self.fail('Finish the test!')

    def test_multiple_users_can_start_lists_at_different_urls(self):
        self.browser.get(self.live_server_url)

        # user1
        user1_text_1 = 'Compre penas de pavão'
        user1_text_2 = 'Use penas de pavão para fazer um fly'
        self.wait_for(self.submit_data_by_post, user1_text_1, max_wait=2)
        self.wait_for(self.submit_data_by_post, user1_text_2, max_wait=2)
        self.wait_for(self.check_for_row_in_list_table, f'2: {user1_text_2}', max_wait=2)
        self.wait_for(self.check_for_row_in_list_table, f'1: {user1_text_1}', max_wait=2)

        user1_list_url = self.browser.current_url
        self.assertRegex(user1_list_url, '/lists/.+')

        self.browser.quit()
        self.browser = webdriver.Firefox()

        # user2
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn(user1_text_1, page_text)
        self.assertNotIn(user1_text_2, page_text)

        user2_text_1 = 'Compre leite'
        self.submit_data_by_post(user2_text_1)
        self.wait_for(self.check_for_row_in_list_table, f'1: {user2_text_1}', max_wait=2)

        user2_list_url = self.browser.current_url
        self.assertRegex(user2_list_url, '/lists/.+')
        self.assertNotEqual(user2_list_url, user1_list_url)

        # user1
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn(user1_text_1, page_text)
        self.assertIn(user2_text_1, page_text)

    def test_layout_and_styling(self):
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )

        text_1 = 'testando'
        self.submit_data_by_post(text_1)
        self.wait_for(self.check_for_row_in_list_table, f'1: {text_1}', max_wait=2)
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )
