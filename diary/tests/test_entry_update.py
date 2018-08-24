from freezegun import freeze_time
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from diary.models import User, Entry
from .base_setup import BaseUserTestCase


class UpdateEntryTestCase(BaseUserTestCase):
    reset_sequences = True

    def setUp(self):
        super(UpdateEntryTestCase, self).setUp()
        self.get_token()
        Entry.objects.create(**self.entry, owner=User.objects.get(pk=1))

    def test_update_post_owner_on_the_same_day(self):
        entry = Entry.objects.get(pk=1)
        response = self.client.put(
            reverse('diary:details', kwargs={'slug_field': entry.slug_field}),
            data={
                'title': 'new title',
                'content': entry.content
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_post_owner_different_day(self):
        now = timezone.now()
        entry = Entry.objects.get(pk=1)
        with freeze_time(now) as frozen_time:
            frozen_time.tick(delta=timedelta(days=1))
            self.client.force_authenticate(user=User.objects.get(pk=1))
            response = self.client.put(
                reverse('diary:details', kwargs={'slug_field': entry.slug_field}),
                data={
                    'title': 'new title',
                    'content': entry.content
                })
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_entry_by_another_user_who_is_not_the_owner(self):
        user2 = User.objects.create_user(**self.user1)
        self.client.force_authenticate(user2)
        entry = Entry.objects.get(pk=1)
        response = self.client.put(
            reverse('diary:details', kwargs={'slug_field': entry.slug_field}),
            data={
                'title': 'new title',
                'content': entry.content
            })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_entry_by_unauthenticated_user(self):
        self.client.credentials()
        entry = Entry.objects.get(pk=1)
        response = self.client.put(
            reverse('diary:details', kwargs={'slug_field': entry.slug_field}),
            data={
                'title': 'new title',
                'content': entry.content
            })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
