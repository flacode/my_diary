from django.urls import reverse
from rest_framework import status
from rest_framework.serializers import ValidationError
from diary.models import User
from diary.exceptions import AccountNotFoundException
from .base_setup import BaseUserTestCase


class UserLoginTestCase(BaseUserTestCase):
    reset_sequences = True

    def test_user_login(self):
        User.objects.create_user(**self.user2)
        response = self.client.post(reverse('diary:login'), data={
            'email': self.user2['email'],
            'password': self.user2['password']
            })
        self.assertContains(response, 'token')
        self.assertTrue(User.objects.get(pk=1).is_logged_in)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_without_activating_account(self):
        self.client.post(reverse('diary:signup'), data=self.user)
        self.client.post(reverse('diary:login'), data={
            'email': self.user['email'],
            'password': self.user['password']
            })
        self.assertRaises(ValidationError)

    def test_user_login_when_not_registered(self):
        self.client.post(reverse('diary:login'), data={
            'email': self.user['email'],
            'password': self.user['password']
            })
        self.assertRaises(AccountNotFoundException)

    def test_user_login_with_wrong_password(self):
        User.objects.create_user(**self.user2)
        response = self.client.post(reverse('diary:login'), data={
            'email': self.user2['email'],
            'password': 'password123'
            })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_without_email(self):
        response = self.client.post(reverse('diary:login'), data={
            'password': 'passwords'
            })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_without_password(self):
        self.client.post(reverse('diary:signup'), data=self.user)
        response = self.client.post(reverse('diary:login'), data={
            'email': self.user['email']
            })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
