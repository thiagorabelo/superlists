from django.conf.urls import url


from . import views


app_name = 'accounts'

urlpatterns = [
    url(r'^send_login_email/$', views.send_login_email, name='send_login_email'),
    url(r'^login/$', views.login, name='login'),
]
