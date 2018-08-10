from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    notification_time = models.TimeField(null=True, blank=True)
    slug_field = models.SlugField(unique=True)
    is_logged_in = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def login(self):
        self.is_logged_in = True
        self.save(update_fields=['is_logged_in'])

    def logout(self):
        self.is_logged_in = False
        self.save(update_fields=['is_logged_in'])

    def __str__(self):
        return self.email
