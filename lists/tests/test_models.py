from django.core.exceptions import ValidationError
from django.test import TestCase

from lists.models import List, Item


class ListAndItemModelTest(TestCase):

    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        text_1 = 'O primeiro item (de todos) da lista'
        first_item.text = text_1
        first_item.list = list_
        first_item.save()

        second_item = Item()
        text_2 = 'O segundo Item'
        second_item.text = text_2
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertCountEqual(first_saved_item.text, text_1)
        self.assertEqual(first_saved_item.list, list_)
        self.assertCountEqual(second_saved_item.text, text_2)
        self.assertEqual(second_saved_item.list, list_)

    def test_can_not_save_empty_list_item(self):
        list_ = List.objects.create()
        item = Item(list=list_, text='')
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()
