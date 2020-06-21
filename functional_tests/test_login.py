import os
import poplib
import re
import time

from django.core import mail

from . import base


TEST_EMAIL = 'edith@testing.org'
SUBJECT = 'Your login link for Goat Testing'


class LoginTest(base.FunctionalTest):

    def wait_for_email(self, test_mail, subject):
        if not self.staging_server:
            email = mail.outbox[0]
            self.assertIn(test_mail, email.to)
            self.assertEqual(email.subject, subject)
            return email.body

        email_id = None
        start = time.time()
        inbox = poplib.POP3_SSL('pop.testing.org')

        try:
            inbox.user(test_mail)
            inbox.pass_(os.environ['EMAIL_USER_PASSWORD'])
            while time.time() - start < 60:
                # obtem as 10 mensagens mais recentes
                count, _ = inbox.stat()

                for i in reversed(range(max(1, count - 10), count + 1)):
                    print('Getting msg:', i)
                    _, lines, _ = inbox.retr(i)
                    lines = [l.decode('utf-8') for l in lines]
                    print(lines)

                    if f'Subject: {subject}' in lines:
                        email_id = i
                        body = '\n'.join(lines)
                        return body
                time.sleep(5)
        finally:
            if email_id:
                inbox.dele(email_id)
            inbox.quit()

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
        body = self.wait_for_email(TEST_EMAIL, SUBJECT)

        # A mensagem contém o link com um url
        self.assertIn('Use this link to log in', body)
        url_search = re.search(r'http://.+/.+$', body)

        if not url_search:
            self.fail(f'Could not find url in email body:\n{body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # Ele clica na url
        self.browser.get(url)

        # Uhull! Estamos logados!
        self.wait_to_be_logged_in(email=TEST_EMAIL)

        # Agora fazemos logout
        self.browser.find_element_by_link_text('Log out').click()

        # Não estamos mais logados
        self.wait_to_be_logged_out(email=TEST_EMAIL)
