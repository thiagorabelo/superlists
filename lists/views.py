from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.views.generic import FormView, CreateView

from .models import List
from .forms import ItemForm, ExistingListItemForm, NewListForm


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


def view_list(request, list_id):
    list_ = List.objects.get(pk=list_id)
    form = ExistingListItemForm()

    if request.method == 'POST':
        data = request.POST.copy()
        data.update({'list': list_.pk})
        form = ExistingListItemForm(data=data)
        if form.is_valid():
            form.save()
            return redirect(list_)

    return render(request, 'lists/list.html', {
        'list': list_,
        'form': form,
    })


def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, 'lists/my_lists.html', {'owner': owner})


def share(request, list_id):
    list_ = List.objects.get(pk=list_id)
    list_.shared_with.add(request.POST['sharee'])
    return redirect(list_)
