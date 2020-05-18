# pylint: disable=too-many-ancestors

from . import base


class ItemValidationTest(base.FunctionalTest):

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
