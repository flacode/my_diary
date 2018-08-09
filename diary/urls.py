from django.urls import path
from . import views

app_name = 'diary'
urlpatterns = [
    path('signup/', views.UserSignUp.as_view(), name='signup'),
    path('activate/', views.ActivateAccount.as_view(), name='activate')
]
