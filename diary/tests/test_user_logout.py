from django.urls import reverse
from rest_framework import status
from diary.models import User
from .base_setup import BaseUserTestCase


class UserLogoutTestCase(BaseUserTestCase):
    reset_sequences = True

    def test_user_logout(self):
        User.objects.create_user(**self.user2)
        login = self.client.post(reverse('diary:login'), data={
            'email': self.user2['email'],
            'password': self.user2['password']
        })
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + login.data['token'])
        response = self.client.get(
            reverse('diary:logout', kwargs={'slug_field': self.user2['slug_field']})
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.get(pk=1).is_logged_in)

    def test_user_logout_without_authentication(self):
        User.objects.create_user(**self.user2)
        response = self.client.get(
            reverse('diary:logout', kwargs={'slug_field': self.user2['slug_field']})
            )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout_with_invalid_slug_field(self):
        response = self.client.get(
            reverse('diary:logout', kwargs={'slug_field': 'jdkbbhhjjbdshbd'})
            )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
