from django.urls import reverse
from django.core import mail
from rest_framework import status
from diary.models import User
from .base_setup import BaseUserTestCase


class UserAccountActivationTestCase(BaseUserTestCase):
    reset_sequences = True

    def test_user_account_activation(self):
        self.client.post(reverse('diary:signup'), data=self.user)
        activation_url = mail.outbox[0].body.split(' ')[-1]
        self.client.get(activation_url)
        active_user = User.objects.get(pk=1)
        self.assertTrue(active_user.is_active)

    def test_user_account_activation_link_is_one_time(self):
        self.client.post(reverse('diary:signup'), data=self.user)
        activation_url = mail.outbox[0].body.split(' ')[-1]
        self.client.get(activation_url)
        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_user_account_activation_with_invalid_token(self):
        response = self.client.get(
            reverse('diary:activate', kwargs={'slug_field': 'jkdjjdddhjjh'}),
            {'token': 'hjhgedgvgdgwegghegvghv'}
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
