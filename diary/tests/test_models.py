from django.test import TransactionTestCase
from diary.models import User


class UserModelTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = {
            'username': 'username',
            'password': 'password',
            'email': 'email'
            }

    def test_user_object_is_created(self):
        user = User.objects.create_user(**self.user)
        self.assertEqual(str(user), self.user['email'])
