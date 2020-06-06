from django.conf.urls import url
from django.contrib.auth.views import logout
from django.urls import reverse_lazy


from . import views


app_name = 'accounts'

urlpatterns = [
    url(r'^send_login_email/$', views.send_login_email, name='send_login_email'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', logout, {'next_page': reverse_lazy('home')}, name='logout'),
]
