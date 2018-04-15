from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import unittest


class NewVisitor(unittest.TestCase):

    def setUp(self):
        self.brower = webdriver.Firefox()
    
    def tearDown(self):
        self.brower.quit()
    
    def test_can_start_a_list_and_retrieve_it_later(self):
        self.brower.get('http://localhost:8000/')

        self.assertIn('To-Do', self.brower.title)
        header_text = self.brower.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        inputbox = self.brower.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        input_text = 'Compre penas de pavão'

        inputbox.send_keys(input_text)
        inputbox.send_keys(Keys.ENTER)

        time.sleep(1)

        table = self.brower.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertTrue(
            any(row.text == f'1: {input_text}' for row in rows)
        )

        self.fail('Finish the test!')

if __name__ == '__main__':
    unittest.main(warnings='ignore')
