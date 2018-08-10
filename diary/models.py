from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_jwt.settings import api_settings


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    notification_time = models.TimeField(null=True, blank=True)
    slug_field = models.SlugField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def generate_token(self):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(self)
        return jwt_encode_handler(payload)
