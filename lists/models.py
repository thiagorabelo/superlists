from django.db import models
from django.core.urlresolvers import reverse


class List(models.Model):
    def get_absolute_url(self):
        return reverse('lists:view_list', kwargs={'list_id': self.pk})

class Item(models.Model):
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None)
