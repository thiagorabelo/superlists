#!/usr/bin/env python

import time

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class NewVisitor(LiveServerTestCase):

    host = 'localhost'
    port = 9000

    @staticmethod
    def sleep(seconds=1):
        time.sleep(seconds)

    def setUp(self):
        self.brower = webdriver.Firefox()

    def tearDown(self):
        self.brower.quit()

    def submit_data_by_post(self, text):
        inputbox = self.brower.find_element_by_id('id_new_item')
        inputbox.send_keys(text)
        inputbox.send_keys(Keys.ENTER)

    def check_for_row_in_list_table(self, row_text):
        table = self.brower.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def test_can_start_a_list_and_retrieve_it_later(self):  # pylint: disable=C0103
        self.brower.get(self.live_server_url)

        self.assertIn('To-Do', self.brower.title)
        header_text = self.brower.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        inputbox = self.brower.find_element_by_id('id_new_item')
        self.assertEqual(inputbox.get_attribute('placeholder'),
                         'Enter a to-do item')

        input_text_1 = 'Compre penas de pavão'
        self.submit_data_by_post(input_text_1)
        self.sleep()
        self.check_for_row_in_list_table(f'1: {input_text_1}')

        input_text_2 = 'Usar penas de pavão para fazer um fly'
        self.submit_data_by_post(input_text_2)
        self.sleep()
        self.check_for_row_in_list_table(f'1: {input_text_1}')
        self.check_for_row_in_list_table(f'2: {input_text_2}')

        self.fail('Finish the test!')
