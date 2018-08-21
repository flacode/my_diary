from datetime import timedelta
from freezegun import freeze_time
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from diary.models import User, Entry
from .base_setup import BaseUserTestCase


class CreateEntryTestCase(BaseUserTestCase):
    reset_sequences = True

    def test_add_one_entry(self):
        self.get_token()
        response = self.client.post(reverse('diary:create-list'), data={
            'title': self.entry['title'],
            'content': self.entry['content']
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_more_than_one_entry_with_different_titles(self):
        self.get_token()
        self.client.post(reverse('diary:create-list'), data={
            'title': self.entry2['title'],
            'content': self.entry2['content']
        })
        response = self.client.post(reverse('diary:create-list'), data={
            'title': self.entry['title'],
            'content': self.entry['content']
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Entry.objects.all().count(), 2)

    def test_add_more_than_one_entry_with_same_title_on_the_same_day(self):
        self.get_token()
        self.client.post(reverse('diary:create-list'), data={
            'title': self.entry2['title'],
            'content': self.entry2['content']
        })
        response = self.client.post(reverse('diary:create-list'), data={
            'title': self.entry2['title'],
            'content': self.entry['content']
        })
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Entry.objects.all().count(), 1)

    def test_add_entry_without_authentication(self):
        response = self.client.post(reverse('diary:create-list'), data={
            'title': self.entry['title'],
            'content': self.entry['content']
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @freeze_time("2018-08-11")
    def test_add_entry_with_same_name_on_the_same_day(self):
        self.get_token()
        self.client.post(reverse('diary:create-list'), data={
            'title': self.entry2['title'],
            'content': self.entry2['content']
        })
        response = self.client.post(reverse('diary:create-list'), data={
            'title': self.entry2['title'],
            'content': self.entry2['content']
        })
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Entry.objects.all().count(), 1)

    def test_add_entry_with_same_name_on_another_day(self):
        self.get_token()
        now = timezone.now()
        with freeze_time(now) as frozen_time:
            self.client.post(reverse('diary:create-list'), data={
                'title': self.entry2['title'],
                'content': self.entry2['content']
            })
            frozen_time.tick(delta=timedelta(days=1))
            self.client.force_authenticate(user=User.objects.get(pk=1))
            response = self.client.post(reverse('diary:create-list'), data={
                'title': self.entry2['title'],
                'content': self.entry2['content']
            })
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Entry.objects.all().count(), 2)

    def test_same_title_post_for_different_users_on_the_same_day(self):
        self.get_token()
        self.client.post(reverse('diary:create-list'), data={
            'title': self.entry2['title'],
            'content': self.entry2['content']
        })
        user2 = User.objects.create_user(**self.user1)
        self.client.force_authenticate(user2)
        response = self.client.post(reverse('diary:create-list'), data={
            'title': self.entry2['title'],
            'content': self.entry2['content']
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Entry.objects.all().count(), 2)

    def test_unique_title_is_case_sensitive(self):
        self.get_token()
        self.client.post(reverse('diary:create-list'), data={
            'title': self.entry2['title'],
            'content': self.entry2['content']
        })
        response = self.client.post(reverse('diary:create-list'), data={
            'title': self.entry2['title'].upper(),
            'content': self.entry2['content']
        })
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Entry.objects.all().count(), 1)
