# pylint: disable=too-many-ancestors

from . import base


class LayoutAndStylingTest(base.FunctionalTest):

    def test_layout_and_styling(self):
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        inputbox = self.browser.find_element_by_id('id_new_item')

        self.wait_for(
            self.assertAlmostEqual,
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10,
            max_wait=3
        )

        text_1 = 'testando'
        self.submit_data_by_post(text_1)
        self.wait_for(self.check_for_row_in_list_table, f'1: {text_1}', max_wait=2)
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.wait_for(
            self.assertAlmostEqual,
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10,
            max_wait=3
        )
