from django.urls import path
from .views import UserLoginView, UserLogoutView, register, profile_edit


app_name = 'accounts'


urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile_edit, name='profile_edit'),
]


