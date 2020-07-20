from .base import FunctionalTest


class MyListTest(FunctionalTest):

    def test_logged_in_users_list_are_saved_as_my_list(self):
        email = 'edith@testing.org'
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_out(email)

        # Edith quer ficar logada
        self.create_pre_authenticated_session(email)
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_in(email)

    def test_logged_in_users_are_salved_as_my_lists(self):
        # Edith é uma usuária logada
        email = 'edith@testing.org'
        self.create_pre_authenticated_session(email)

        # Edith acessa a página inicial e comela uma lista
        self.browser.get(self.live_server_url)
        list_1_item_1 = 'Estrias Reticuladas'
        list_1_item_2 = 'Imanentizar a escatologia'  # Edith tem cada ideia bizarra
        self.add_list_item(list_1_item_1)
        self.add_list_item(list_1_item_2)
        first_list_url = self.browser.current_url

        # Ela percebe o link "My lists" pela primeira vez
        self.browser.find_element_by_link_text('My lists').click()

        # Ela fica feliz em ver que sua lista está lá, nomeada de
        # acordo com o primeiro item da lista
        self.until(max_wait=5).wait(lambda: self.browser.find_element_by_link_text(list_1_item_1))
        self.browser.find_element_by_partial_link_text(list_1_item_1).click()
        self.until(max_wait=5).wait(
            lambda: self.assertEqual(self.browser.current_url, first_list_url)
        )

        # Ela decide iniciar uma nova lista, somente para conferir
        self.browser.get(self.live_server_url)
        list_2_item_1 = 'Clicar em vacas'  # https://en.wikipedia.org/wiki/Cow_Clicker
        self.add_list_item(list_2_item_1)
        second_list_url = self.browser.current_url

        # Em "My lists", sua nova lista aparece
        self.browser.find_element_by_partial_link_text('My lists').click()
        self.until(max_wait=5).wait(
            lambda: self.browser.find_element_by_link_text(list_2_item_1)
        )
        self.browser.find_element_by_partial_link_text(list_2_item_1).click()
        self.until(max_wait=5).wait(
            lambda: self.assertEqual(self.browser.current_url, second_list_url)
        )

        # Faz logout e aopção "My lists" desaparece
        self.browser.find_element_by_link_text('Log out').click()
        self.until(max_wait=5).wait(
            lambda: self.assertEmpty(self.browser.find_elements_by_link_text('My lists'))
        )
