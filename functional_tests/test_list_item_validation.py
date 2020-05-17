# pylint: disable=too-many-ancestors

from . import base


class ItemValidationTest(base.FunctionalTest):

    # @skip("Este teste está incompleto")
    def test_can_not_add_empty_list_items(self):
        # Usuário acessa a página inicial e tenta inserir um
        # item vazio na lista teclando enter na caixa de diálogo
        # vazia
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_text').send_keys(base.Keys.ENTER)

        # A página inicial é atualizada e há uma mensagem de erro
        # informando que itens da lista não podem ser vazios.
        self.until(max_wait=3, step_wait=1).wait(
            lambda: self.assertEqual(
                self.browser.find_element_by_css_selector('.has-error').text,
                "You can't have an empty list item"
            )
        )

        # Ele tenta novamente com um texto para o item e desta vez
        # funciona
        text_1 = 'Compre leite'
        self.until(max_wait=3, step_wait=1).wait(self.submit_data_by_post, text_1)
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'1: {text_1}')

        # De sacanagem, ela tenta submeter um segundo item em branco
        # na lista
        self.browser.find_element_by_id('id_text').send_keys(base.Keys.ENTER)

        # Ele recebe um aviso semelhante na página da lista.
        self.until(max_wait=3, step_wait=1).wait(
            lambda: self.assertEqual(
                self.browser.find_element_by_css_selector('.has-error').text,
                "You can't have an empty list item"
            )
        )

        # Isso pode ser corrigido preenchendo o item com um texto
        text_2 = 'Faça chá'
        self.until(max_wait=3, step_wait=1).wait(self.submit_data_by_post, text_2)
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'1: {text_1}')
        self.until(max_wait=3).wait(self.check_for_row_in_list_table, f'2: {text_2}')
