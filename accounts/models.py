from django.contrib.auth import models as auth_models
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Token(models.Model):
    email = models.EmailField()
    uid = models.CharField(max_length=37)


class ListUserManager(auth_models.BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = '?'
        user.save(using=self._db)
        return user

    def create_user(self, email, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, **extra_fields)

    def create_superuser(self, email, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, **extra_fields)


class ListUser(auth_models.AbstractUser):  # pylint: disable=model-no-explicit-unicode
    username_validator = None
    username = None
    first_name = None
    last_name = None
    get_full_name = None
    get_short_name = None

    email = models.EmailField(_('email address'), primary_key=True)

    objects = auth_models.UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
