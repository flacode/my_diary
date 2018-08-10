from django.utils.text import slugify
from django.test import TransactionTestCase
from django.urls import reverse
from django.core import mail
from rest_framework.test import APIClient
from diary.models import User


class BaseUserTestCase(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = {
            'username': 'username',
            'email': 'email@email.com',
            'password': 'password',
            'confirm_password': 'password'
        }
        self.user2 = {
            'username': 'username',
            'email': 'email@email.com',
            'password': 'password',
            'slug_field': slugify('username'),
            'is_active': True
        }

    def get_password_url(self):
        User.objects.create_user(**self.user2)
        self.client.post(reverse('diary:password-reset'), data={
            'email': self.user2['email'],
            })
        return mail.outbox[0].body.split(' ')[-1]
