from django.urls import reverse
from rest_framework import status
from diary.models import User, Entry
from .base_setup import BaseUserTestCase


class DeleteEntryTestCase(BaseUserTestCase):
    reset_sequences = True

    def setUp(self):
        super(DeleteEntryTestCase, self).setUp()
        self.get_token()
        Entry.objects.create(**self.entry, owner=User.objects.get(pk=1))

    def test_delete_post_by_owner(self):
        entry = Entry.objects.get(pk=1)
        entries_before = Entry.objects.all().count()
        response = self.client.delete(
            reverse('diary:details', kwargs={'slug_field': entry.slug_field})
            )
        entries_after = Entry.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertLess(entries_after, entries_before)

    def test_delete_entry_by_another_user_who_is_not_the_owner(self):
        user2 = User.objects.create_user(**self.user1)
        self.client.force_authenticate(user2)
        entry = Entry.objects.get(pk=1)
        response = self.client.delete(
            reverse('diary:details', kwargs={'slug_field': entry.slug_field})
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_entry_by_unauthenticated_user(self):
        self.client.credentials()
        entry = Entry.objects.get(pk=1)
        response = self.client.delete(
            reverse('diary:details', kwargs={'slug_field': entry.slug_field}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
