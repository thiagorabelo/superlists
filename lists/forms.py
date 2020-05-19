from django.core.exceptions import ValidationError
from django import forms

from .models import Item


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

    def save(self, commit=True):  # pylint: disable=arguments-differ
        return forms.ModelForm.save(self, commit=commit)

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as ex:
            ex.error_dict = {'text': [DUPLICATE_ITEM_ERROR]}
            self._update_errors(ex)
