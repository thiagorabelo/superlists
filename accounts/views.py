from django.contrib import auth
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse

from accounts.models import Token


def send_login_email(request):
    email = request.POST['email']
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        f"{reverse('accounts:login')}?token={str(token.uid)}"
    )
    message_body = f'Use this link to log in:\n\n{url}'
    send_mail(
        'Your login link for Goat Testing',
        message_body,
        'noreply@goat.testing.org',
        [email]
    )
    messages.success(
        request,
        "Check your email, we've sent you a link you can use to log in."
    )
    return redirect('home')


def login(request):
    user = auth.authenticate(uid=request.GET.get('token'))
    if user:
        auth.login(request, user)
    return redirect('/')
