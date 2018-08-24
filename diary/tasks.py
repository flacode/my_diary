from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


@shared_task
def notification_email(username, email, time):
    html_message = render_to_string(
        'diary/notification.html',
        {
            'username': username,
        })
    text_message = "Welcome {}. You set a reminder to update your diary at {} everyday".format(
        username,
        time
    )
    message = EmailMultiAlternatives(
        'Reminder {}: MyDiary'.format(time),
        text_message, settings.EMAIL_HOST_USER,
        [email])
    message.attach_alternative(html_message, "text/html")
    message.send()
