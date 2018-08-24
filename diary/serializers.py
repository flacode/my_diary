from smtplib import SMTPException
from rest_framework import serializers
from django.utils.text import slugify
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings
from .helpers import send_email, create_periodic_task, delete_periodic_task
from . import exceptions
from .models import User, Entry


class AuthenticationModelSerializer(serializers.ModelSerializer):
    """Base class with validations for ModelSerializers."""
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password should have more than 8 characters")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data


class UserSignupSerializer(AuthenticationModelSerializer):
    """Serializer for user sign up"""
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
            )
        user.set_password(validated_data['password'])
        user.slug_field = slugify(user.username, allow_unicode=True)
        try:
            send_email(user)
            user.save()
            return user
        except SMTPException:
            raise exceptions.EmailNotSentException


class UserLoginSerializer(serializers.ModelSerializer):
    """Serializer for user login."""
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if user.is_active:
                return value
            raise serializers.ValidationError("User account is not yet activated, "
                                              "please check your email for activation "
                                              "instructions.")
        except User.DoesNotExist:
            raise exceptions.AccountNotFoundException

    def validate(self, data):
        credentials = {
            'email': data['email'],
            'password': data['password']
        }
        user = authenticate(**credentials)
        if user:
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            user.login()
            return {
                'slug_field': user.slug_field,
                'email': user.email,
                'token': token,
            }
        raise exceptions.InvalidCredentialsException


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serialiser to request for password reset using email or username"""
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)

    def validate_username(self, value):
        try:
            User.objects.get(username=value)
            return value
        except User.DoesNotExist:
            raise exceptions.AccountNotFoundException

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise exceptions.AccountNotFoundException


class PasswordResetHandlerSerializer(AuthenticationModelSerializer):
    """Serialiser to handle for password reset for a user"""
    username = serializers.ReadOnlyField()
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class EntrySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Entry
        fields = ('title', 'content', 'owner', 'created', 'modified')
        read_only_fields = ('created', 'modified')

    def update(self, instance, validated_data):
        if instance.is_modifiable:
            instance.title = validated_data.get('title', instance.title)
            instance.content = validated_data.get('content', instance.title)
            instance.save()
            return instance
        raise exceptions.CanNotModifyEntryException


class NotificationsSerializer(serializers.Serializer):
    notification_time = serializers.TimeField(
        format='%H:%M', input_formats=['%H:%M'], required=False
        )
    detail = serializers.CharField(read_only=True)

    class Meta:
        fields = ('notification_time', 'detail')

    def create(self, validated_data):
        user = self.context['user']
        time = validated_data.get('notification_time', None)
        if time:
            detail = create_periodic_task(user, str(time))
        else:
            detail = delete_periodic_task(user)
        return {
            'notification_time': time,
            'detail': detail
        }
