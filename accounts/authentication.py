from django.contrib.auth import get_user_model

from accounts.models import Token


User = get_user_model()


class PasswordlessAuthenticationBackend:

    def authenticate(self, uid):
        try:
            token = Token.objects.get(uid=uid)
            return User.objects.get(email=token.email)
        except User.DoesNotExist:
            return User.objects.create(email=token.email)
        except Token.DoesNotExist:
            return None

    def get_user(self, email):
        try:
            return User.objects.get(pk=email)
        except User.DoesNotExist:
            return None
