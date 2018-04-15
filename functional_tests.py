from selenium import webdriver
import unittest


class NewVisitor(unittest.TestCase):

    def setUp(self):
        self.brower = webdriver.Firefox()
    
    def tearDown(self):
        self.brower.quit()
    
    def test_can_start_a_list_and_retrieve_it_later(self):
        self.brower.get('http://localhost:8000/')

        self.assertIn('To-Do', self.brower.title)
        self.fail('Finish the test')


if __name__ == '__main__':
    unittest.main(warnings='ignore')
