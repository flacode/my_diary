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
        self.user1 = {
            'username': 'username1',
            'email': 'email1@email.com',
            'password': 'password',
            'slug_field': slugify('username1'),
            'is_active': True,
            'is_logged_in': True
        }
        self.entry = {
            'title': 'entry 1',
            'content': 'content for entry 1'
        }
        self.entry2 = {
            'title': 'entry 2',
            'content': 'content for entry 2'
        }

    def get_password_url(self):
        User.objects.create_user(**self.user2)
        self.client.post(reverse('diary:password-reset'), data={
            'email': self.user2['email'],
            })
        return mail.outbox[0].body.split(' ')[-1]

    def get_token(self):
        User.objects.create_user(**self.user2)
        login = self.client.post(reverse('diary:login'), data={
            'email': self.user2['email'],
            'password': self.user2['password']
        })
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + login.data['token'])
