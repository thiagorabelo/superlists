from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.authentication import PasswordlessAuthenticationBackend
from accounts.models import Token


User = get_user_model()


EMAIL = 'edith@example.com'


class AuthenticationTest(TestCase):

    def test_returns_None_if_no_such_token(self):  # pylint: disable=invalid-name
        result = PasswordlessAuthenticationBackend().authenticate('no-such-token')
        self.assertIsNone(result)

    def test_returns_new_user_with_correct_email_if_token_exists(self):
        token = Token.objects.create(email=EMAIL)
        new_user = PasswordlessAuthenticationBackend().authenticate(token.uid)
        user = User.objects.get(email=EMAIL)
        self.assertEqual(new_user, user)

    def test_returns_existing_user_with_correct_email_if_token_exists(self):
        existing_user = User.objects.create(email=EMAIL)
        token = Token.objects.create(email=EMAIL)
        user = PasswordlessAuthenticationBackend().authenticate(token.uid)
        self.assertEqual(user, existing_user)

    def test_get_user_by_email(self):
        User.objects.create(email='another@example.com')
        desired_user = User.objects.create(email=EMAIL)
        found_user = PasswordlessAuthenticationBackend().get_user(EMAIL)
        self.assertEqual(found_user, desired_user)

    def test_returns_None_if_no_user_with_that_email(self):  # pylint: disable=invalid-name
        self.assertIsNone(
            PasswordlessAuthenticationBackend().get_user(EMAIL)
        )
