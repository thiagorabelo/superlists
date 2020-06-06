import re

from django.core import mail

from . import base


TEST_EMAIL = 'user@example.com'
SUBJECT = 'Your login link for Goat Testing'


class LoginTest(base.FunctionalTest):

    def test_can_get_email_link_to_log_in(self):
        # O usuário entra no site e se dá conta que há uma
        # seção de "Log in" na barra de navegação.
        # Essa sessão sugere que ela insira seu endereço de
        # email. Sabendo que não se trata de phishing, ele
        # faz isso.
        self.browser.get(self.live_server_url)
        self.submit_data_by_post(TEST_EMAIL, id_input='id_email')

        # Uma mensagem aparece informando-lhe que um email foi
        # enviado
        self.until(max_wait=3).wait(lambda: self.assertIn(
            'Check your email',
            self.browser.find_element_by_tag_name('body').text
        ))

        # Ele verifica seu e-mail e encontra uma mensagem
        email = mail.outbox[0]
        self.assertIn(TEST_EMAIL, email.to)
        self.assertEqual(email.subject, SUBJECT)

        # A mensagem contém o link com um url
        self.assertIn('Use this link to log in', email.body)
        url_search = re.search(r'http://.+/.+$', email.body)

        if not url_search:
            self.fail(f'Could not find url in email body:\n{email.body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # Ele clica na url
        self.browser.get(url)

        # Uhull! Estamos logados!
        self.until(max_wait=3).wait(
            lambda: self.browser.find_element_by_link_text('Log out')
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(TEST_EMAIL, navbar.text)

        # Agora fazemos logout
        self.browser.find_element_by_link_text('Log out').click()

        # Não estamos mais logados
        self.until(max_wait=3).wait(
            lambda: self.browser.find_element_by_name('email')
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertNotIn(TEST_EMAIL, navbar.text)
