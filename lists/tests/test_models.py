from lists.views import new_list
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from lists.models import List, Item

# pylint: disable=invalid-name

User = get_user_model()


class ListAndItemModelTest(TestCase):

    def test_default_text(self):
        item = Item()
        self.assertEqual(item.text, '')

    def test_item_is_related_to_list(self):
        list_ = List.objects.create()
        item = Item()
        item.list = list_
        item.save()
        self.assertIn(item, list_.item_set.all())

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

    def test_duplicate_items_are_invalid(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='bla')
        with self.assertRaises(ValidationError):
            item = Item(list=list_, text='bla')
            item.full_clean()

    def test_CAN_save_same_item_to_different_lists(self):
        list1 = List.objects.create()
        list2 = List.objects.create()
        Item.objects.create(list=list1, text='bla')
        item = Item(list=list2, text='bla')
        item.full_clean()  # Não deve gerar erro

    def test_list_ordering(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='i1')
        item2 = Item.objects.create(list=list1, text='item 2')
        item3 = Item.objects.create(list=list1, text='3')

        self.assertEqual(
            list(Item.objects.all()),
            [item1, item2, item3]
        )

    def test_string_representation(self):
        item = Item(text='some text')
        self.assertEqual(str(item), 'some text')


class ListModelTest(TestCase):

    def test_get_absolute_url(self):
        list_ = List.objects.create()
        self.assertEqual(list_.get_absolute_url(), f'/lists/{list_.pk}/')

    def test_lists_can_have_owners(self):
        List(owner=User())  # não deve gerar erro

    def test_list_owner_is_optional(self):
        List().full_clean()  # não deve gerar erro  # não deve gerar erro

    def test_list_name_is_first_item_text(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='first item')
        Item.objects.create(list=list_, text='second item')
        self.assertEqual(list_.name, 'first item')

    def test_create_new_creates_list_and_first_item(self):
        item_text = 'new item text'
        List.create_new(first_item_text=item_text)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, item_text)
        new_list = List.objects.first()
        self.assertEqual(new_item.list, new_list)

    def test_create_new_optionally_saves_owner(self):
        user = User.objects.create()
        List.create_new(first_item_text='new item text', owner=user)
        new_list = List.objects.first()
        self.assertEqual(new_list.owner, user)

    def test_create_new_returns_new_list_object(self):
        item_text = 'new item text'
        returned = List.create_new(first_item_text=item_text)
        new_list = List.objects.first()
        self.assertEqual(returned, new_list)

    def test_can_share_with_another_user(self):
        owner = User.objects.create(email='a@b.com')
        friend = User.objects.create(email='c@d.com')

        list_ = List.objects.create(owner=owner)
        list_.shared_with.add(friend)
        list_in_db = List.objects.get(pk=list_.pk)

        self.assertIn(list_, friend.shared_lists.all())
        self.assertIn(friend, list_in_db.shared_with.all())
