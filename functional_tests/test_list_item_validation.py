# pylint: disable=too-many-ancestors

from . import base


class ItemValidationTest(base.FunctionalTest):

    # @skip("Este teste está incompleto")
    def test_can_not_add_empty_list_items(self):
        # Usuário acessa a página inicial e tenta inserir um
        # item vazio na lista teclando enter na caixa de diálogo
        # vazia
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('id_new_item').send_keys(base.Keys.ENTER)

        # A página inicial é atualizada e há uma mensagem de erro
        # informando que itens da lista não podem ser vazios.
        self.wait_for(
            self.assertEqual,
            self.browser.find_element_by_css_selector('.has-error').text,
            "You can't have an empty list item"
        ).run(max_wait=2)

        # Ele tenta novamente com um texto para o item e desta vez
        # funciona
        text_1 = 'Buy milk'
        self.submit_data_by_post('Buy milk')
        self.wait_for(self.check_for_row_in_list_table, f'1: {text_1}')

        # De sacanagem, ela tenta submeter um segundo item em branco
        # na lista
        self.browser.find_element_by_id('id_new_item').send_keys(base.Keys.ENTER)

        # Ele recebe um aviso semelhante na página da lista.
        self.wait_for(
            self.assertEqual,
            self.browser.find_element_by_css_selector('.has-error').text,
            "You can't have an empty list item"
        ).run(max_wait=2)

        # Isso pode ser corrigido preenchendo o item com um texto
        text_2 = 'Make tea'
        self.submit_data_by_post(text_2)
        self.wait_for(self.check_for_row_in_list_table, f'1: {text_1}')
        self.wait_for(self.check_for_row_in_list_table, f'2: {text_2}')
