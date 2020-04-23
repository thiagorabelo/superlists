#!/usr/bin/env python
# pylint: disable=C0111

import time
import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class NewVisitor(unittest.TestCase):

    def setUp(self):
        self.brower = webdriver.Firefox()

    def tearDown(self):
        self.brower.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):  # pylint: disable=C0103
        self.brower.get('http://localhost:8000/')

        self.assertIn('To-Do', self.brower.title)
        header_text = self.brower.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        inputbox = self.brower.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        input_text_1 = 'Compre penas de pavão'
        inputbox.send_keys(input_text_1)
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        input_text_2 = 'Usar penas de pavão para fazer um fly'
        inputbox = self.brower.find_element_by_id('id_new_item')
        inputbox.send_keys(input_text_2)
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # input('pause...')
        table = self.brower.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')

        self.assertIn(f'1: {input_text_1}', [row.text for row in rows])
        self.assertIn(f'2: {input_text_2}', [row.text for row in rows])

        self.fail('Finish the test!')

if __name__ == '__main__':
    unittest.main(warnings='ignore')
