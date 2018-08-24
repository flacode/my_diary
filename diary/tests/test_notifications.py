from django.urls import reverse
from django.core import mail
from rest_framework import status
from django_celery_beat.models import PeriodicTask
from diary.tasks import notification_email
from .base_setup import BaseUserTestCase


class NotificationsTestCase(BaseUserTestCase):
    reset_sequences = True

    def setUp(self):
        super(NotificationsTestCase, self).setUp()
        self.get_token()

    def test_set_notification_time(self):
        response = self.client.post(
            reverse('diary:notify', kwargs={'slug_field': self.user2['slug_field']}),
            data={'notification_time': '12:30'})
        task = PeriodicTask.objects.get(pk=1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(task.enabled)

    def test_unset_notification_task(self):
        self.client.post(
            reverse('diary:notify', kwargs={'slug_field': self.user2['slug_field']}),
            data={'notification_time': '12:30'})
        task_before = PeriodicTask.objects.all().count()
        response = self.client.post(
            reverse('diary:notify', kwargs={'slug_field': self.user2['slug_field']}))
        task_after = PeriodicTask.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(task_before, task_after)

    def test_set_notification_time_without_value(self):
        response = self.client.post(
            reverse('diary:notify', kwargs={'slug_field': self.user2['slug_field']}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_email_is_sent(self):
        notification_email(username='username', email='email@email.com', time='12:90')
        self.assertEqual(len(mail.outbox), 1)

    def test_set_notification_time_without_authentication(self):
        self.client.credentials()
        response = self.client.post(
            reverse('diary:notify', kwargs={'slug_field': self.user2['slug_field']}),
            data={'notification_time': '12:30'})
        tasks = PeriodicTask.objects.all().count()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(tasks, 0)
