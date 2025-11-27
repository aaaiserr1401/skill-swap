from django.urls import path
from .views import (
    UserLoginView, UserLogoutView, register, profile_edit, profile_detail,
    user_detail, send_request, user_search,
    exchange_list, exchange_create, exchange_accept, exchange_decline, exchange_confirm, inbox_requests, exchange_detail,
)


app_name = 'accounts'


urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile_edit, name='profile_edit'),
    path('me/', profile_detail, name='profile_detail'),
    path('users/', user_search, name='user_search'),
    path('users/<int:user_id>/', user_detail, name='user_detail'),
    path('users/<int:user_id>/send/', send_request, name='send_request'),
    # Exchanges
    path('exchanges/', exchange_list, name='exchange_list'),
    path('exchanges/inbox/', inbox_requests, name='inbox_requests'),
    path('exchanges/create/', exchange_create, name='exchange_create'),
    path('exchanges/<int:pk>/', exchange_detail, name='exchange_detail'),
    path('exchanges/<int:pk>/accept/', exchange_accept, name='exchange_accept'),
    path('exchanges/<int:pk>/decline/', exchange_decline, name='exchange_decline'),
    path('exchanges/<int:pk>/confirm/', exchange_confirm, name='exchange_confirm'),
]


