# pylint: disable=too-many-ancestors

from . import base


class LayoutAndStylingTest(base.FunctionalTest):

    def test_layout_and_styling(self):
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        def assert_inputbox_is_in_center(id_element='id_text', expected=512, delta=10):
            # Para cada tentativa busque o input novamente, pois
            # parece que os valores em location ou size parecem
            # estar cacheados.
            input_box = self.get_item_input_box(id_element)
            x_pos = input_box.location['x']
            width = input_box.size['width']
            self.assertAlmostEqual(x_pos + width / 2, expected, delta=delta)

        self.until(max_wait=3, step_wait=1).wait(assert_inputbox_is_in_center)

        text_1 = 'testando'
        self.submit_data_by_post(text_1)
        self.until(max_wait=2).wait(self.check_for_row_in_list_table, f'1: {text_1}')
        self.until(max_wait=3, step_wait=1).wait(assert_inputbox_is_in_center)
