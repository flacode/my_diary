from django.test import TransactionTestCase
from django.urls import reverse
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status
from diary.models import User


class UserRegistrationTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
        self.user = {
            'username': 'username',
            'email': 'email@email.com',
            'password': 'password',
            'confirm_password': 'password'
        }

    def test_user_registration_creates_user_object(self):
        users_before = User.objects.all().count()
        response = self.client.post(reverse('diary:signup'), data=self.user)
        users_after = User.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(users_after, users_before)

    def test_user_is_sent_email_after_registration(self):
        self.client.post(reverse('diary:signup'), data=self.user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Account confirmation: MyDiary')

    def test_user_registration_with_same_account(self):
        self.client.post(reverse('diary:signup'), data=self.user)
        response = self.client.post(reverse('diary:signup'), data=self.user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_with_different_passwords(self):
        self.user['confirm_password'] = 'password123'
        response = self.client.post(reverse('diary:signup'), data=self.user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_with_short_password(self):
        self.user.update(password='pass', confirm_password='pass')
        response = self.client.post(reverse('diary:signup'), data=self.user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAccountActivationTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
        self.user = {
            'username': 'username',
            'email': 'email@email.com',
            'password': 'password',
            'confirm_password': 'password'
        }

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
