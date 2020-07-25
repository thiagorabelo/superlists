"""superlists URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from . import views


app_name = 'lists'


urlpatterns = [
    url(r'^new$', views.NewListView.as_view(), name='new_list'),
    url(r'^(?P<pk>\d+)/$', views.ViewAndAddToList.as_view(), name='view_list'),
    url(r'^users/(?P<email>.+)/$', views.MyListsView.as_view(), name='my_lists'),
    url(r'^(?P<list_id>\d+)/share$', views.share, name='share'),
]
