from smtplib import SMTPException
from rest_framework import serializers
from django.utils.text import slugify
from .helpers import send_email
from .exceptions import EmailNotSentException, AccountNotFoundException
from .models import User


class AuthenticationModelsSerializer(serializers.ModelSerializer):
    """Base class with validations for ModelSerializers."""
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password should have more than 8 characters")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data


class AuthenticationSerializer(serializers.Serializer):
    """Base class with validations for Serializers."""
    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise AccountNotFoundException


class UserSignupSerializer(AuthenticationModelsSerializer):
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
            raise EmailNotSentException


class UserLoginSerializer(AuthenticationSerializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = User.objects.get(email=data['email'])
        if user.is_active:
            return user
        raise serializers.ValidationError("User account is not yet activated, "
                                          "please check your email for activation instructions.")


class PasswordResetRequestSerializer(AuthenticationSerializer):
    """Serialiser to request for password reset using email or username"""
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    user = None

    def validate_username(self, value):
        try:
            User.objects.get(username=value)
            return value
        except User.DoesNotExist:
            raise AccountNotFoundException


class PasswordResetHandlerSerializer(AuthenticationModelsSerializer):
    """SSerialiser to handle for password reset for a user"""
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
