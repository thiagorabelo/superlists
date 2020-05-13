# pylint: disable=too-many-ancestors

from unittest import skip

from . import base


class ItemValidationTest(base.FunctionalTest):

    @skip("Este teste está incompleto")
    def test_can_not_add_empty_list_items(self):
        # Usuário acessa a página inicial e tenta inserir um
        # item vazio na lista teclando enter na caixa de diálogo
        # vazia

        # A página inicial é atualizada e há uma mensagem de erro
        # informando que itens da lista não podem ser vazios.

        # Ele tenta novamente com um texto para o item e desta vez
        # funciona

        # De sacanagem, ela tenta submeter um segundo item em branco
        # na lista

        # Ele recebe um aviso semelhante na página da lista.

        # Isso pode ser corrigido preenchendo o item com um texto

        self.fail('Escreva-me')
