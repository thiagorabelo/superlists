import uuid

from django.db import models
from django.contrib import auth


auth.signals.user_logged_in.disconnect(auth.models.update_last_login)


class User(models.Model):
    email = models.EmailField(primary_key=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    is_anonymous = False
    is_authenticated = True

    def __str__(self):
        return self.email

    def __repr__(self):
        return f'<User: email="{self.email}">'


class Token(models.Model):
    email = models.EmailField()
    uid = models.CharField(max_length=37, default=uuid.uuid4)
