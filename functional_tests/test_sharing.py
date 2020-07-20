from selenium import webdriver
from .base import FunctionalTest


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
        self.browser.get(self.live_server_url)
        self.add_list_item('Get help')

        # Ela percebe que há uma opção "Share this list"
        share_box = self.browser.find_element_by_css_selector(
            'input[name="share"]'
        )
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'your-friend@example.com'
        )
