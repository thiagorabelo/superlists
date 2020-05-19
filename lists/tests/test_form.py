from django.test import TestCase

from lists.forms import (
    DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR,
    ExistingListItemForm, ItemForm,
)
from lists.models import List, Item


class ItemFormTest(TestCase):

    def test_form_item_input_has_placeholder_and_css_classes(self):
        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_validation_form_blank_items(self):
        form = ItemForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

    def test_form_save_handle_saving_to_a_list(self):
        list_ = List.objects.create()
        text_1 = 'do me'
        form = ItemForm(data={'text': text_1}, initial={'list': list_})
        new_item = form.save(for_list=list_)
        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, text_1)
        self.assertEqual(new_item.list, list_)


class ExistingListItemFormTest(TestCase):

    def test_form_renders_item_text_input(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(initial={'list': list_})
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_form_validation_for_bank_lines(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(data={'text': ''}, initial={'list': list_})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_ITEM_ERROR])

    def test_form_validation_for_duplicate_items(self):
        text = 'no twins!'
        list_ = List.objects.create()
        Item.objects.create(list=list_, text=text)
        form = ExistingListItemForm(data={'text': text, 'list': list_.pk})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [DUPLICATE_ITEM_ERROR])

    def test_form_save(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(data={'list': list_.pk, 'text': 'hi'})
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.first())