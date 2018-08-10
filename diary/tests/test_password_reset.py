from django.urls import reverse
from django.core import mail
from rest_framework import status
from diary.models import User
from .base_setup import BaseUserTestCase


class UserPasswordReset(BaseUserTestCase):
    reset_sequences = True

    def test_user_request_reset_password_with_email(self):
        User.objects.create_user(**self.user2)
        response = self.client.post(reverse('diary:password-reset'), data={
            'email': self.user2['email'],
            })
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_user_request_reset_password_with_username(self):
        User.objects.create_user(**self.user2)
        response = self.client.post(reverse('diary:password-reset'), data={
            'username': self.user2['username'],
            })
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_user_password_reset_request_sends_email(self):
        User.objects.create_user(**self.user2)
        self.client.post(reverse('diary:password-reset'), data={
            'email': self.user2['email'],
            })
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password reset: MyDiary')

    def test_user_password_reset_request_without_account_email(self):
        response = self.client.post(reverse('diary:password-reset'), data={
            'email': self.user['email'],
            })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_password_reset_request_without_account_username(self):
        response = self.client.post(reverse('diary:password-reset'), data={
            'username': self.user['username'],
            })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_reset_handler(self):
        password_url = self.get_password_url()
        response = self.client.put(
            password_url,
            data={'password': 'new_password', 'confirm_password': 'new_password'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_handler_with_the_same_link(self):
        password_url = self.get_password_url()
        self.client.put(
            password_url,
            data={'password': 'new_password', 'confirm_password': 'new_password'}
        )
        response = self.client.put(
            password_url,
            data={'password': 'new_password', 'confirm_password': 'new_password'}
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_password_reset_handler_with_different_passwords(self):
        password_url = self.get_password_url()
        response = self.client.put(
            password_url,
            data={'password': 'new_password', 'confirm_password': 'new_password123'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_handler_with_short_passwords(self):
        password_url = self.get_password_url()
        response = self.client.put(
            password_url,
            data={'password': 'new', 'confirm_password': 'new'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
