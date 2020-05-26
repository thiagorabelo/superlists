from django.core.exceptions import ValidationError
from django import forms

from .models import Item, List


EMPTY_ITEM_ERROR = "You can't have a empty list item"
DUPLICATE_ITEM_ERROR = "You've already got this in your list"


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('text',)
        widgets = {
            'text': forms.fields.TextInput(attrs={
                'placeholder': 'Enter a to-do item',
                'class': 'form-control input-lg'
            })
        }
        error_messages = {
            'text': {'required': EMPTY_ITEM_ERROR}
        }

    def save(self, for_list, commit=True):  # pylint: disable=arguments-differ
        self.instance.list = for_list
        return super().save(commit)


class ExistingListItemForm(ItemForm):
    class Meta(ItemForm.Meta):
        fields = ('list', 'text')

    def __init__(self, data=None, list_=None, **kwargs):
        if data and 'list' not in data:
            if not list_:
                raise ValueError('list must be in data or in list_ parameter')
            data = data.copy()

            if isinstance(list_, List):
                data.update({'list': list_.pk})
            else:
                data.update({'list': list_})

        super().__init__(data=data, **kwargs)

    def save(self, commit=True):  # pylint: disable=arguments-differ
        return forms.ModelForm.save(self, commit=commit)

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as ex:
            ex.error_dict = {'text': [DUPLICATE_ITEM_ERROR]}
            self._update_errors(ex)
