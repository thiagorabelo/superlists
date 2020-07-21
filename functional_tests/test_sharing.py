from .base import FunctionalTest
from .list_page import ListPage
from .my_lists_page import MyListsPage


MARTA_EMAIL = 'marta@testing.org'
JONAS_EMAIL = 'jonas@testing.org'


def quit_if_possible(browser):
    try:
        browser.quit()
    except:
        pass


class SharingTest(FunctionalTest):

    def test_can_share_a_list_with_another_user(self):
        # Marta é uma usuária logada
        self.create_pre_authenticated_session(MARTA_EMAIL)
        marta_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(marta_browser))

        # Seu amigo Jonas também está no site de listas
        jonas_browser = self.get_browser()
        self.addCleanup(lambda: quit_if_possible(jonas_browser))
        self.browser = jonas_browser
        self.create_pre_authenticated_session(JONAS_EMAIL)

        # Marta acessa a página inicial e começa uma lista
        self.browser = marta_browser
        marta_item_1 = 'Get Help'
        self.browser.get(self.live_server_url)
        list_page = ListPage(self).add_list_item(marta_item_1)

        # Ela percebe que há uma opção "Share this list"
        share_box = list_page.get_share_box()
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'your-friend@example.com'
        )

        # Ela compartilha sua lista.
        # A página é atualizada para informar que a lista foi compartilhada
        # com Jonas
        list_page.share_list_with(JONAS_EMAIL)

        # Jonas agora acessa a página de listas com seu navegador
        self.browser = jonas_browser
        MyListsPage(self).go_to_my_list_page()

        # Ele vê a lista de Marta!
        self.browser.find_element_by_link_text(marta_item_1).click()

        # Na página de lista, Jonas pode ver que a lista é de Marta
        self.until(max_wait=5).wait(lambda: self.assertEqual(
            list_page.get_list_owner(),
            MARTA_EMAIL
        ))

        # Ele adiciona um item na lista
        marta_item_2 = 'Hi Marta!'
        list_page.add_list_item(marta_item_2)

        # Quando Marta atualiza a página, ela vê o acrescimo feito por Jonas
        self.browser = marta_browser
        self.browser.refresh()
        list_page.wait_for_row_in_list_table(marta_item_2, 2)
