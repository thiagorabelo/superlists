from .base import FunctionalTest

class MyListsPage:

    def __init__(self, test:FunctionalTest):
        self.test = test

    def go_to_my_list_page(self):
        self.test.browser.get(self.test.live_server_url)
        self.test.browser.find_element_by_link_text('My lists').click()
        self.test.until(max_wait=5).wait(
            lambda: self.test.assertEqual(
                self.test.browser.find_element_by_tag_name('h1').text,
                'My lists'
            )
        )
