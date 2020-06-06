from unittest.mock import patch, call

from django.test import TestCase

from accounts.models import Token


class SendLoginEmailViewTest(TestCase):

    def test_redirects_to_home_page(self):
        response = self.client.post('/accounts/send_login_email/', data={
            'email': 'edith@example.com',
        })
        self.assertRedirects(response, '/')


    @patch('accounts.views.send_mail')
    def test_send_mail_to_address_from_post(self, mock_send_mail):
        mail = 'edith@example.com'
        self.client.post('/accounts/send_login_email/', data={
            'email': mail,
        })

        self.assertTrue(mock_send_mail.called)
        (subject, body, from_mail, to_list), _ = mock_send_mail.call_args
        self.assertEqual(subject, 'Your login link for Goat Testing')
        self.assertIn('Use this link to log in', body)
        self.assertEqual(from_mail, 'noreply@goat.testing.org')
        self.assertEqual(to_list, [mail])

    def test_adds_success_message(self):
        email = 'edith@example.com'
        response = self.client.post('/accounts/send_login_email/', data={
            'email': email,
        }, follow=True)

        message = list(response.context['messages'])[0]
        self.assertEqual(
            message.message,
            "Check your email, we've sent you a link you can use to log in."
        )
        self.assertEqual(message.tags, 'success')

    @patch('accounts.views.messages')
    def test_adds_success_message_with_mocks(self, mock_messages):
        email = 'edith@example.com'
        response = self.client.post('/accounts/send_login_email/', data={
            'email': email,
        })  # com mock não carece de follow=True

        expected = "Check your email, we've sent you a link you can use to log in."

        self.assertEqual(
            mock_messages.success.call_args,
            call(response.wsgi_request, expected)
        )

    def test_create_token_associated_with_email(self):
        email = 'edith@example.com'
        self.client.post('/accounts/send_login_email/', data={
            'email': email
        })

        token = Token.objects.first()
        self.assertEqual(token.email, email)

    @patch('accounts.views.send_mail')
    def test_sends_link_to_login_using_token_uid(self, mock_send_mail):
        email = 'edith@example.com'
        self.client.post('/accounts/send_login_email/', data={
            'email': email
        })
        token = Token.objects.first()
        expected_url = f'http://testserver/accounts/login/?token={token.uid}'
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertIn(expected_url, body)


@patch('accounts.views.auth')
class LoginViewTest(TestCase):

    def test_redirects_to_home_page(self, mock_auth):
        response = self.client.get('/accounts/login/?token=abcd123')
        self.assertRedirects(response, '/')

    def test_calls_authenticate_with_uid_from_get_request(self, mock_auth):
        self.client.get('/accounts/login/?token=abcd123')
        self.assertEqual(
            mock_auth.authenticate.call_args,
            call(uid='abcd123')
        )

    def test_calls_auth_login_with_user_if_there_is_no_one(self, mock_auth):
        response = self.client.get('/accounts/login/?token=abcd123')
        self.assertEqual(
            mock_auth.login.call_args,
            call(response.wsgi_request, mock_auth.authenticate.return_value)
        )

    def test_does_not_login_if_user_is_not_authenticated(self, mock_auth):
        mock_auth.authenticate.return_value = None
        self.client.get('/accounts/login/?token=abcd123')
        self.assertFalse(mock_auth.login.called)
