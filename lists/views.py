from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.views.generic import FormView, CreateView, DetailView, ListView

from .models import List, Item
from .forms import ItemForm, ExistingListItemForm, NewListForm


# pylint: disable=attribute-defined-outside-init
# pylint: disable=too-many-ancestors


User = get_user_model()


class HomePageView(FormView):
    template_name = 'lists/home.html'
    form_class = ItemForm


class NewListView(CreateView):
    template_name = 'lists/home.html'
    form_class = NewListForm

    def form_valid(self, form):
        self.object = form.save(owner=self.request.user)
        return redirect(self.get_success_url())


class ViewAndAddToList(DetailView, CreateView):
    model = List
    template_name = 'lists/list.html'
    form_class = ExistingListItemForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'list_': self.object.pk})
        kwargs.update({'instance': Item()})
        return kwargs

    def get_form(self, form_class=None):
        if self.object is None:
            self.object = self.get_object()
        return super().get_form(form_class=form_class)


class MyListsView(ListView):
    model = List
    template_name = 'lists/my_lists.html'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['owner'] = User.objects.get(email=self.kwargs['email'])
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner__email=self.kwargs['email'])


def share(request, list_id):
    list_ = List.objects.get(pk=list_id)
    list_.shared_with.add(request.POST['sharee'])
    return redirect(list_)
