from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings
from .tokens import ACTIVATIONTOKEN, PASSWORDRESETTOKEN


def send_email(user):
    path = reverse('diary:activate', kwargs={'slug_field': user.slug_field})
    token = ACTIVATIONTOKEN.make_token(user)
    activation_url = "{}{}?token={}".format(settings.SITE_ROOT, path, token)
    html_message = render_to_string(
        'diary/activate.html',
        {
            'username': user.username,
            'activation_url': activation_url
        })
    text_message = "Welcome {}. Please use the following link to activate your account {}".format(
        user.username,
        activation_url
    )
    message = EmailMultiAlternatives(
        'Account confirmation: MyDiary',
        text_message, settings.EMAIL_HOST_USER,
        [user.email])
    message.attach_alternative(html_message, "text/html")
    message.send()


def send_password_reset_email(user):
    token = PASSWORDRESETTOKEN.make_token(user)
    path = reverse(
        'diary:password-rest-handler',
        kwargs={'slug_field': user.slug_field, 'token': token}
        )
    password_url = "{}{}".format(settings.SITE_ROOT, path)
    html_message = render_to_string(
        'diary/password_reset.html',
        {
            'username': user.username,
            'password_url': password_url
        })
    text_message = "Hello {}. Please use the following link to reset yor password {}".format(
        user.username,
        password_url
    )
    message = EmailMultiAlternatives(
        'Password reset: MyDiary',
        text_message, settings.EMAIL_HOST_USER,
        [user.email])
    message.attach_alternative(html_message, "text/html")
    message.send()
