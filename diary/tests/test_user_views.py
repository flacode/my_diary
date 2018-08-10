from django.test import TransactionTestCase
from django.urls import reverse
from django.utils.text import slugify
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.serializers import ValidationError
from diary.models import User
from diary.exceptions import AccountNotFoundException


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


class UserRegistrationTestCase(BaseUserTestCase):
    reset_sequences = True

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


class UserLoginTestCase(BaseUserTestCase):
    reset_sequences = True

    def test_user_login(self):
        User.objects.create_user(**self.user2)
        response = self.client.post(reverse('diary:login'), data={
            'email': self.user2['email'],
            'password': self.user2['password']
            })
        self.assertContains(response, 'token')
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
