from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.exceptions import APIException


class EmailNotSentException(APIException):
    """ Exception thrown when the confirmation email can not be sent """
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'not_registered'


def send_email(user):
    path = reverse('diary:activate')
    activation_url = "{}{}?token={}".format(settings.SITE_ROOT, path, user.slug_field)
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
