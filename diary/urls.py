from rest_framework_jwt.views import obtain_jwt_token
from django.urls import path
from . import views

app_name = 'diary'
urlpatterns = [
    path('auth/signup/', views.UserSignUp.as_view(), name='signup'),
    path('auth/activate/<str:slug_field>/', views.ActivateAccount.as_view(), name='activate'),
    path('auth/login/', views.LoginUser.as_view(), name='login'),
    path('auth/passwordreset/', views.PasswordResetRequest.as_view(), name='password-reset'),
    path(
        'auth/passwordreset/<str:slug_field>/<str:token>/',
        views.PasswordResetHandler.as_view(),
        name='password-rest-handler'
        ),
    path('<str:slug_field>/logout/', views.UserLogout.as_view(), name='logout'),
    path('entries/', views.EntryCreateListAPIView.as_view(), name='create-list'),
    path('entries/<str:slug_field>/', views.EntryAPIView.as_view(), name='details')
]
