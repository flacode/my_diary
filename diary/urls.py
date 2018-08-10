from rest_framework_jwt.views import obtain_jwt_token
from django.urls import path
from . import views

app_name = 'diary'
urlpatterns = [
    path('signup/', views.UserSignUp.as_view(), name='signup'),
    path('activate/<str:slug_field>/', views.ActivateAccount.as_view(), name='activate'),
    path('login/', views.LoginUser.as_view(), name='login')
]
