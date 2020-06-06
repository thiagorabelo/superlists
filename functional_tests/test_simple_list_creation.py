# pylint: disable=too-many-ancestors

from selenium import webdriver

from . import base


class NewVisitorTest(base.FunctionalTest):

    def test_can_start_a_list_for_one_user(self):  # pylint: disable=C0103
        self.browser.get(self.live_server_url)

        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        inputbox = self.browser.find_element_by_id('id_text')
        self.assertEqual(inputbox.get_attribute('placeholder'),
                         'Enter a to-do item')

        input_text_1 = 'Compre penas de pavão'
        self.submit_data_by_post(input_text_1)
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'1: {input_text_1}')

        input_text_2 = 'Usar penas de pavão para fazer um fly'
        self.submit_data_by_post(input_text_2)
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'1: {input_text_1}')
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'2: {input_text_2}')

        # self.fail('Finish the test!')

    def test_multiple_users_can_start_lists_at_different_urls(self):
        self.browser.get(self.live_server_url)

        # user1
        user1_text_1 = 'Compre penas de pavão'
        user1_text_2 = 'Use penas de pavão para fazer um fly'
        self.until(max_wait=3).wait(self.submit_data_by_post, user1_text_1)
        self.until(max_wait=3).wait(self.submit_data_by_post, user1_text_2)
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'2: {user1_text_2}')
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'1: {user1_text_1}')

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
        self.until(max_wait=2).wait(self.check_for_row_in_list_table, f'1: {user2_text_1}')

        user2_list_url = self.browser.current_url
        self.assertRegex(user2_list_url, '/lists/.+')
        self.assertNotEqual(user2_list_url, user1_list_url)

        # user1
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn(user1_text_1, page_text)
        self.assertIn(user2_text_1, page_text)
