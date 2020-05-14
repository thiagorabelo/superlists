# pylint: disable=missing-docstring

from django.utils.html import escape
from django.test import TestCase

from lists.models import Item, List


class HomePageTest(TestCase):

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'lists/home.html')


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
        other_list = List.objects.create()  # pylint: disable=unused-variable
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.pk}/')

        self.assertEqual(response.context['list'], correct_list)

    def test_can_save_a_POST_request_to_an_existing_list(self):  # pylint: disable=invalid-name
        other_list = List.objects.create()  # pylint: disable=unused-variable
        correct_list = List.objects.create()

        new_list_item_1 = 'Um novo item para uma lista existente'

        self.client.post(
            f'/lists/{correct_list.pk}/',
            data={'item_text': new_list_item_1}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, new_list_item_1)
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirect_to_list_view(self):  # pylint: disable=invalid-name
        other_list = List.objects.create()  # pylint: disable=unused-variable
        correct_list = List.objects.create()

        new_list_item_1 = 'Um novo item para uma lista existente'

        response = self.client.post(
            f'/lists/{correct_list.pk}/',
            data={'item_text': new_list_item_1}
        )

        self.assertRedirects(response, f'/lists/{correct_list.pk}/')


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

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response = self.client.post('/lists/new', data={'item_text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/home.html')
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)

    def test_invalid_list_items_arent_salved(self):
        self.client.post('/lists/new', data={'item_text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
