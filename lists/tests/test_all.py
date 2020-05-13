# pylint: disable=missing-docstring

from django.test import TestCase

from .models import Item, List


class HomePageTest(TestCase):

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'lists/home.html')


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


class ListViewTest(TestCase):

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.pk}/')
        self.assertTemplateUsed(response, 'lists/list.html')

    def test_display_only_items_for_that_list(self):
        correct_list = List.objects.create()
        correct_list_item_1 = 'itemey 1'
        correct_list_item_2 = 'itemey 2'
        Item.objects.create(text=correct_list_item_1, list=correct_list)
        Item.objects.create(text=correct_list_item_2, list=correct_list)

        other_list = List.objects.create()
        other_list_itemey_1 = 'other list itemey 1'
        other_list_itemey_2 = 'other list itemey 2'
        Item.objects.create(text=other_list_itemey_1, list=other_list)
        Item.objects.create(text=other_list_itemey_2, list=other_list)

        response = self.client.get(f'/lists/{correct_list.pk}/')

        self.assertContains(response, correct_list_item_1)
        self.assertContains(response, correct_list_item_2)
        self.assertNotContains(response, other_list_itemey_1)
        self.assertNotContains(response, other_list_itemey_2)

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.pk}/')

        self.assertEqual(response.context['list'], correct_list)


class NewListTest(TestCase):

    def test_can_save_a_POST_request(self):  # pylint: disable=invalid-name
        new_item_text = 'A new list item'
        self.client.post('/lists/new', data={'item_text': new_item_text})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, new_item_text)

    def test_redirect_after_POST(self):  # pylint: disable=invalid-name
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.pk}/')


class NewItemTest(TestCase):

    def test_can_save_a_POST_request_to_an_existing_list(self):  # pylint: disable=invalid-name
        other_list = List.objects.create()  # pylint: disable=unused-variable
        correct_list = List.objects.create()

        new_list_item_1 = 'Um novo item para uma lista existente'

        self.client.post(
            f'/lists/{correct_list.pk}/add_item',
            data={'item_text': new_list_item_1}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, new_list_item_1)
        self.assertEqual(new_item.list, correct_list)

    def test_redirect_to_list_view(self):
        other_list = List.objects.create()  # pylint: disable=unused-variable
        correct_list = List.objects.create()

        new_list_item_1 = 'Um novo item para uma lista existente'

        response = self.client.post(
            f'/lists/{correct_list.pk}/add_item',
            data={'item_text': new_list_item_1}
        )

        self.assertRedirects(response, f'/lists/{correct_list.pk}/')
