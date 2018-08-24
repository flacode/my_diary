from django.urls import reverse
from rest_framework import status
from diary.models import User, Entry
from .base_setup import BaseUserTestCase


class RetrieveEntriesTestCase(BaseUserTestCase):
    reset_sequences = True

    def setUp(self):
        super(RetrieveEntriesTestCase, self).setUp()
        self.get_token()
        Entry.objects.create(**self.entry, owner=User.objects.get(pk=1))
        Entry.objects.create(**self.entry2, owner=User.objects.get(pk=1))

    def test_retrieve_all_entries_owner(self):
        response = self.client.get(reverse('diary:create-list'))
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_all_entries_not_the_owner(self):
        user2 = User.objects.create_user(**self.user1)
        self.client.force_authenticate(user2)
        response = self.client.get(reverse('diary:create-list'))
        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_all_entries_when_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(reverse('diary:create-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_single_entry_owner(self):
        entry = Entry.objects.get(pk=1)
        response = self.client.get(
            reverse('diary:details', kwargs={'slug_field': entry.slug_field})
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_single_entry_not_owner(self):
        user2 = User.objects.create_user(**self.user1)
        self.client.force_authenticate(user2)
        entry = Entry.objects.get(pk=1)
        response = self.client.get(
            reverse('diary:details', kwargs={'slug_field': entry.slug_field}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_entry_not_exist(self):
        response = self.client.get(reverse('diary:details', kwargs={'slug_field': 'jkdhdbhhjdb'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_entry_unauthenticated(self):
        self.client.credentials()
        entry = Entry.objects.get(pk=1)
        response = self.client.get(
            reverse('diary:details', kwargs={'slug_field': entry.slug_field}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
