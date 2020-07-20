from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse


class List(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    @property
    def name(self):
        return self.item_set.first().text

    def get_absolute_url(self):
        return reverse('lists:view_list', kwargs={'list_id': self.pk})

    @classmethod
    def create_new(cls, first_item_text, owner=None):
        list_ = cls.objects.create(owner=owner)
        Item.objects.create(text=first_item_text, list=list_)
        return list_


class Item(models.Model):
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None)

    class Meta:
        ordering = ('pk',)
        unique_together = ('list', 'text')

    def __str__(self):
        return self.text
