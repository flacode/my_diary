from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    notification_time = models.TimeField(null=True, blank=True)
    slug_field = models.SlugField(unique=True)

    def __str__(self):
        return self.email
