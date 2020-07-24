from unittest.mock import Mock, patch

from django.test import TestCase

from lists.forms import (
    DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR,
    ExistingListItemForm, ItemForm, NewListForm,
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


class ExistingListItemFormTest(TestCase):

    def test_call_form_with_expected_parameters(self):
        list_ = List.objects.create()
        ExistingListItemForm(data={'list': list_.pk, 'text': 'virgi'})
        with self.assertRaises(ValueError):
            ExistingListItemForm(data={'text': 'virgi'})

    def test_form_renders_item_text_input(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(initial={'list': list_})
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_form_validation_for_bank_lines(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(data={'text': '', 'list': list_})
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


class NewListFormTest(TestCase):

    @patch('django.forms.models.BaseModelForm.save')
    @patch('lists.forms.List.create_new')
    def test_save_creates_new_list_from_post_data_if_user_not_authenticated(
        self, create_new_list_for_item, mockBaseModelForm_save
    ):
        item_text = 'new item text'
        owner = Mock(is_authenticated=False)
        form = NewListForm(data={'text': item_text})
        form.save_m2m = Mock()

        form.is_valid()
        form.save(owner=owner)

        create_new_list_for_item.assert_called_once_with(
            mockBaseModelForm_save.return_value,
            owner=None
        )

    @patch('django.forms.models.BaseModelForm.save')
    @patch('lists.forms.List.create_new')
    def test_save_creates_new_list_with_owner_if_user_authenticated(
        self, create_new_list_for_item, mockBaseModelForm_save
    ):
        item_text = 'new item text'
        owner = Mock(is_authenticated=True)
        form = NewListForm(data={'text': item_text})
        form.save_m2m = Mock()

        form.is_valid()
        form.save(owner=owner)

        create_new_list_for_item.assert_called_once_with(
            mockBaseModelForm_save.return_value,
            owner=owner
        )


    @patch('django.forms.models.BaseModelForm.save')
    @patch('lists.forms.List.create_new')
    def test_save_returns_new_list_object(
        self, mock_create_new_list_for_item, mockBaseModelForm_save
    ):
        item_text = 'new item text'
        form = NewListForm(data={'text': item_text})
        form.save_m2m = Mock()
        owner = Mock(is_authenticated=True)

        form.is_valid()
        list_ = form.save(owner=owner)

        mock_create_new_list_for_item.assert_called_once_with(
            mockBaseModelForm_save.return_value,
            owner=owner
        )

        self.assertEqual(
            mock_create_new_list_for_item.return_value,
            list_
        )