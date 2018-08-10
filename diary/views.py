from smtplib import SMTPException
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import User
from .tokens import ACTIVATIONTOKEN, PASSWORDRESETTOKEN
from .exceptions import EmailNotSentException
from .helpers import send_password_reset_email
from . import serializers


class UserSignUp(generics.CreateAPIView):
    serializer_class = serializers.UserSignupSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        result = {
            'user': serializer.data,
            'detail': "Successfully registered, please check your email to activate your account."
        }
        return Response(result, status=status.HTTP_201_CREATED)


class ActivateAccount(APIView):
    def get(self, request, slug_field=None):
        token = request.GET.get('token')
        try:
            user = User.objects.get(slug_field=slug_field)
            if ACTIVATIONTOKEN.check_token(user, token):
                user.is_active = True
                user.save()
                message = "You account has been activated. Please login."
                status_code = status.HTTP_202_ACCEPTED
            else:
                message = "Your account is already activated, Please login."
                status_code = status.HTTP_409_CONFLICT
            result = {
                'message': message,
                'login_url': settings.SITE_ROOT + reverse('diary:login'),
            }
            return Response(result, status=status_code)
        except User.DoesNotExist:
            result = {
                'detail': "User account does not exist"
            }
            return Response(result, status=status.HTTP_404_NOT_FOUND)


class LoginUser(generics.GenericAPIView):

    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credentials = {
            'email': request.data['email'],
            'password': request.data['password']
        }
        user = authenticate(request, **credentials)
        if user:
            response_data = {
                'token': user.generate_token,
                'user': serializers.UserSignupSerializer(user, context={'request': request}).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class PasswordResetRequest(generics.GenericAPIView):
    serializer_class = serializers.PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email', None)
        username = serializer.data.get('username', None)
        if username:
            email = User.objects.get(username=username).email
        try:
            send_password_reset_email(User.objects.get(email=email))
        except SMTPException:
            raise EmailNotSentException
        response = {
            'user': username or email,
            'detail': 'Instructions for password reset have been sent your email.'
        }
        return Response(response, status=status.HTTP_202_ACCEPTED)


class PasswordResetHandler(generics.UpdateAPIView):
    serializer_class = serializers.PasswordResetHandlerSerializer
    queryset = User.objects.all()
    lookup_field = 'slug_field'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if PASSWORDRESETTOKEN.check_token(instance, kwargs['token']):
            self.perform_update(serializer)
            response = {
                'user': serializers.PasswordResetHandlerSerializer(instance).data,
                'detail': 'Password successfully reset.'
            }
            return Response(response, status=status.HTTP_200_OK)
        message = 'Password reset link has expired, please request for a new one.'
        return Response({'detail': message}, status=status.HTTP_409_CONFLICT)
