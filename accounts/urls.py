from django.urls import path
from .views import (
    UserLoginView, UserLogoutView, register, profile_edit, profile_detail,
    exchange_list, exchange_create, exchange_accept, exchange_decline, exchange_confirm,
)


app_name = 'accounts'


urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile_edit, name='profile_edit'),
    path('me/', profile_detail, name='profile_detail'),
    # Exchanges
    path('exchanges/', exchange_list, name='exchange_list'),
    path('exchanges/create/', exchange_create, name='exchange_create'),
    path('exchanges/<int:pk>/accept/', exchange_accept, name='exchange_accept'),
    path('exchanges/<int:pk>/decline/', exchange_decline, name='exchange_decline'),
    path('exchanges/<int:pk>/confirm/', exchange_confirm, name='exchange_confirm'),
]


