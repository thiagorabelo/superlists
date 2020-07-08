from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect

from .models import List
from .forms import ItemForm, ExistingListItemForm


User = get_user_model()


def home_page(request):
    return render(request, 'lists/home.html', {'form': ItemForm()})


def new_list(request):
    form = ItemForm(data=request.POST)

    if form.is_valid():
        list_ = List()
        if request.user.is_authenticated:
            list_.owner = request.user
        list_.save()
        form.save(for_list=list_)
        return redirect(list_)
    return render(request, 'lists/home.html', {'form': form})


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
