from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import User
from .serializers import UserSignupSerializer


class UserSignUp(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        result = {
            'user': serializer.data,
            'message': "Successfully registered, please check your email to activate your account."
        }
        return Response(result, status=status.HTTP_201_CREATED)


class ActivateAccount(APIView):
    def get(self, request):
        token = request.GET.get('token')
        try:
            user = User.objects.get(slug_field=token)
            user.is_active = True
            user.save()
            result = {
                'url': 'login url',
                'message': "You account has been activated. Please login."
            }
            return Response(result, status=status.HTTP_202_ACCEPTED)
        except User.DoesNotExist:
            result = {
                'message': "User account does not exist"
            }
            return Response(result, status=status.HTTP_404_NOT_FOUND)
