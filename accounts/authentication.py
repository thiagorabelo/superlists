import sys

from .models import ListUser, Token


class PasswordlessAuthenticationBackend(object):

    def authenticate(self, uid):
        print(f'uid={uid}', file=sys.stderr)

        if not Token.objects.filter(uid=uid).exists():
            print('No token found', file=sys.stderr)
            return None

        token = Token.objects.get(uid=uid)
        print('Got token', file=sys.stderr)

        try:
            user = ListUser.objects.get(email=token.email)
            print('Got user', file=sys.stderr)
            return user
        except ListUser.DoesNotExist:
            print('New user', file=sys.stderr)
            return ListUser.objects.create(email=token.email)

    def get_user(self, email):
        return ListUser.objects.get(email=email)
