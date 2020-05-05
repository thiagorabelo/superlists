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
        response = self.client.get('/lists/the-only-list-in-the-world/')
        self.assertTemplateUsed(response, 'lists/list.html')

    def test_display_all_items(self):
        list_ = List.objects.create()
        Item.objects.create(text='itemey 1', list=list_)
        Item.objects.create(text='itemey 2', list=list_)

        response = self.client.get('/lists/the-only-list-in-the-world/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')


class NewListTest(TestCase):

    def test_can_save_a_POST_request(self):  # pylint: disable=invalid-name
        new_item_text = 'A new list item'
        self.client.post('/lists/new', data={'item_text': new_item_text})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, new_item_text)

    def test_redirect_after_POST(self):  # pylint: disable=invalid-name
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        self.assertRedirects(response, '/lists/the-only-list-in-the-world/')
