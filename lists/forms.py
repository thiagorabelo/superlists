from django import forms

from .models import Item


EMPTY_ITEM_ERROR = "You can't have a empty list item"


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
