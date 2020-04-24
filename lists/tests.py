# pylint: disable=missing-docstring

from django.test import TestCase

from .models import Item


class HomePageTest(TestCase):

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_can_save_a_POST_request(self):  # pylint: disable=invalid-name
        new_item_text = 'A new list item'
        response = self.client.post('/', data={'item_text': new_item_text})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, new_item_text)

        # self.assertIn('A new list item', response.content.decode())
        # self.assertTemplateUsed(response, 'lists/home.html')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_redirect_after_POST(self):  # pylint: disable=invalid-name
        response = self.client.post('/', data={'item_text': 'A new list item'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_only_save_items_when_necessary(self):
        self.client.get('/')
        self.assertEqual(Item.objects.count(), 0)

    def test_display_all_list_items(self):
        text_1, text_2 = 'itemy 1', 'itemy 2'
        Item.objects.create(text=text_1)
        Item.objects.create(text=text_2)

        response = self.client.get('/')

        self.assertIn(text_1, response.content.decode())
        self.assertIn(text_2, response.content.decode())


class ItemModelTest(TestCase):

    def test_saving_and_retrieving_items(self):
        first_item = Item()
        text_1 = 'O primeiro item (de todos) da lista'
        first_item.text = text_1
        first_item.save()

        second_item = Item()
        text_2 = 'O segundo Item'
        second_item.text = text_2
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertCountEqual(first_saved_item.text, text_1)
        self.assertCountEqual(second_saved_item.text, text_2)
