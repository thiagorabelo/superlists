# pylint: disable=too-many-ancestors

from unittest import skip

from . import base


class ItemValidationTest(base.FunctionalTest):

    def get_error_element(self, css_selector='.has-error'):
        return self.browser.find_element_by_css_selector(css_selector)


    # @skip("Este teste está incompleto")
    def test_can_not_add_empty_list_items(self):
        # Usuário acessa a página inicial e tenta inserir um
        # item vazio na lista teclando enter na caixa de diálogo
        # vazia
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys(base.Keys.ENTER)

        # O navegador intercepta a requisição e não carrega a
        # página da lista
        self.until(max_wait=1).wait(
            lambda: self.browser.find_element_by_css_selector('#id_text:invalid')
        )

        # O usuário começa a digitar um texto para o novo item e o
        # erro desaparece
        text_1 = 'Compre leite'
        self.get_item_input_box().send_keys(text_1)
        self.until(max_wait=1).wait(
            lambda: self.browser.find_element_by_css_selector('#id_text:valid')
        )

        # O usuário pode submeter o item com sucesso
        self.get_item_input_box().send_keys(base.Keys.ENTER)
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'1: {text_1}')

        # De sacanagem, o usuário escroto tenta submeter um segundo item
        # em branco na lista
        self.get_item_input_box().send_keys(base.Keys.ENTER)

        # Novamente o navegador acha isso um absurdo e não concorda
        # em continuar com tal disparate.
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'1: {text_1}')
        self.until(max_wait=1).wait(
            lambda: self.browser.find_element_by_css_selector('#id_text:invalid')
        )

        # O usuário baixa o facho e resolve seguir as normas,
        # preenchendo o item com um texto.
        text_2 = 'Faça chá'
        self.get_item_input_box().send_keys(text_2)
        self.until(max_wait=1).wait(
            lambda: self.browser.find_element_by_css_selector('#id_text:valid')
        )

        # Pronto, agora está tudo como esperado.
        self.get_item_input_box().send_keys(base.Keys.ENTER)
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'1: {text_1}')
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'2: {text_2}')

    def test_cannot_add_duplicate_items(self):
        self.browser.get(self.live_server_url)

        text_1 = 'Compre galochas'

        self.add_list_item(text_1)

        self.submit_data_by_post(text_1)
        self.until(max_wait=5).wait(lambda: self.assertEqual(
            self.get_error_element().text,
            "You've already got this in your list"
        ))

    #@skip
    def test_error_messages_are_cleared_on_input(self):
        text_1 = 'Brincadeiras muito grossas'
        self.browser.get(self.live_server_url)
        self.submit_data_by_post(text_1)
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'1: {text_1}')
        self.submit_data_by_post(text_1)

        self.until(max_wait=3).wait(lambda: self.assertTrue(
            self.get_error_element().is_displayed()
        ))

        self.get_item_input_box().send_keys('a')

        self.until(max_wait=2).wait(lambda: self.assertFalse(
            self.get_error_element().is_displayed()
        ))
