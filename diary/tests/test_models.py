from django.test import TransactionTestCase
from diary.models import User, Entry


class BaseSetUp(TransactionTestCase):
    def setUp(self):
        self.user = {
            'username': 'username',
            'password': 'password',
            'email': 'email'
            }


class UserModelTestCase(BaseSetUp):
    reset_sequences = True

    def test_user_object_is_created(self):
        user = User.objects.create_user(**self.user)
        self.assertEqual(str(user), self.user['email'])


class EntryModelTestCase(BaseSetUp):
    reset_sequences = True

    def test_entry_object_created(self):
        new_entry = {
            'title': 'entry 1',
            'content': 'content for entry 1',
            'owner': User.objects.create_user(**self.user)
        }
        entry = Entry.objects.create(**new_entry)
        self.assertEqual(str(entry), new_entry['title'])
