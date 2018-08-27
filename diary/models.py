from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
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

    def save(self, *args, **kwargs):
        self.slug_field = slugify(self.username, allow_unicode=True)
        super(User, self).save(*args, **kwargs)


class Entry(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diary'
        )
    title = models.CharField(max_length=100)
    slug_field = models.SlugField(unique=True)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def is_modifiable(self):
        days = (timezone.now() - self.created).days
        if days == 0:
            return True
        return False

    def save(self, *args, **kwargs):
        now = datetime.now()
        second = now.strftime('%f')
        day = now.strftime('%j')
        self.slug_field = slugify(self.title+str(day)+str(second))
        super(Entry, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
