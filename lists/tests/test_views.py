# pylint: disable=missing-docstring

from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.utils.html import escape
from django.test import TestCase
from django.test.client import RequestFactory

from lists.models import Item, List
from lists.forms import (
    DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR,
    ExistingListItemForm, ItemForm
)
from lists.views import NewListView


User = get_user_model()


class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):

    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(
            f'/lists/{list_.pk}/',
            data={'text': ''}
        )

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
            data={'text': new_list_item_1}
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
            data={'text': new_list_item_1}
        )

        self.assertRedirects(response, f'/lists/{correct_list.pk}/')

    def test_display_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.pk}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        text1 = 'textey'
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='textey')
        response = self.client.post(
            f'/lists/{list1.pk}/',
            data={'text': text1}
        )

        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'lists/list.html')
        self.assertEqual(Item.objects.all().count(), 1)


class NewListIntegratedTest(TestCase):

    def test_can_save_a_POST_request(self):  # pylint: disable=invalid-name
        new_item_text = 'A new list item'
        self.client.post('/lists/new', data={'text': new_item_text})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, new_item_text)

    def test_redirect_after_POST(self):  # pylint: disable=invalid-name
        response = self.client.post('/lists/new', data={'text': 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.pk}/')

    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/home.html')

    def test_validation_errors_shown_on_home_page(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_for_invalid_input_passes_form_to_home(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_invalid_list_items_arent_salved(self):
        self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        email = 'a@b.com'
        user = User.objects.create(email=email)
        self.client.force_login(user)
        self.client.post('/lists/new', data={'text': 'new item'})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)


@patch('lists.views.NewListView.form_class')
class NewListViewUnitTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().post('/lists/new', data={'text': 'new list item'})
        self.request.user = Mock()

    def test_passes_POST_data_to_NewListForm(self, mockNewListForm):
        NewListView.as_view()(self.request)
        mockNewListForm.assert_called_once_with(
            data=self.request.POST,
            initial={},
            prefix=None,
            files=self.request.FILES,
            instance=None
        )

    def test_saves_form_with_owner_if_form_valid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        NewListView.as_view()(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)

    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(self, mock_redirect, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True

        response = NewListView.as_view()(self.request)

        self.assertEqual(response,  mock_redirect.return_value)
        mock_redirect.assert_called_once_with(mock_form.save.return_value.get_absolute_url())

    @patch('lists.views.NewListView.response_class')
    def test_renders_home_template_with_form_if_form_is_invalid(
        self, mock_response_class, mockNewListForm
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False

        response = NewListView.as_view()(self.request)
        response_args, response_kwargs = mock_response_class.call_args

        self.assertEqual(response, mock_response_class.return_value)
        self.assertEqual(self.request, response_kwargs['request'])
        self.assertEqual(['lists/home.html'], response_kwargs['template'])
        self.assertEqual(mock_form, response_kwargs['context']['form'])

    def test_does_not_save_if_form_invalid(self, mockNewListForm):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        NewListView.as_view()(self.request)
        self.assertFalse(mock_form.save.called)


class MyListsTest(TestCase):

    def test_my_lists_url_renders_my_lists_template(self):
        email = 'a@b.com'
        User.objects.create(email=email)
        response = self.client.get(f'/lists/users/{email}/')
        self.assertTemplateUsed(response, 'lists/my_lists.html')

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email='wrong@owner.com')
        correct_user = User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertEqual(response.context['owner'], correct_user)


class NewListViewIntegratedTest(TestCase):

    def post_new_list(self, item_text):
        return self.client.post('/lists/new', data={'text': item_text})

    def test_can_save_a_POST_request(self):
        item_text = 'A new list item'
        response = self.post_new_list(item_text)
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, item_text)

    def test_for_invalid_input_doenst_save_but_shows_errors(self):
        response = self.post_new_list('')
        self.assertEqual(List.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        item_text = 'new item'
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.post_new_list(item_text)
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)


class ShareListTest(TestCase):

    def test_sharing_a_list_via_post(self):
        owner = User.objects.create(email='edith@testing.org')
        friend = User.objects.create(email='james@testing.org')

        item_text = 'new item text'
        list_ = List.create_new(item_text, owner=owner)

        response = self.client.post(
            f'/lists/{list_.pk}/share',
            data={'sharee': friend.email}
        )

        self.assertIn(list_, friend.shared_lists.all())

    def test_redirects_after_POST(self):
        owner = User.objects.create(email='edith@testing.org')
        friend = User.objects.create(email='james@testing.org')

        item_text = 'new item text'
        list_ = List.create_new(item_text, owner=owner)

        response = self.client.post(
            f'/lists/{list_.pk}/share',
            data={'sharee': friend.email}
        )

        self.assertRedirects(response, f'/lists/{list_.pk}/')
