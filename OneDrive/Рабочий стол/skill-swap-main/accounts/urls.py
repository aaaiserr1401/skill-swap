from django.urls import path
from .views import (
    UserLoginView, UserLogoutView, register, profile_edit, profile_detail,
    user_detail, send_request, user_search,
    exchange_list, exchange_create, exchange_accept, exchange_decline, exchange_confirm, inbox_requests, exchange_detail,
    make_me_superuser,
)
from .admin_views import (
    admin_dashboard, admin_users, admin_user_detail,
    admin_skills, admin_exchanges, admin_exchange_detail,
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
    # Admin panel
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', admin_users, name='admin_users'),
    path('admin-panel/users/<int:user_id>/', admin_user_detail, name='admin_user_detail'),
    path('admin-panel/skills/', admin_skills, name='admin_skills'),
    path('admin-panel/exchanges/', admin_exchanges, name='admin_exchanges'),
    path('admin-panel/exchanges/<int:exchange_id>/', admin_exchange_detail, name='admin_exchange_detail'),
    # TEMP: promote current user to superuser in DEBUG
    path('make-me-super/', make_me_superuser, name='make_me_superuser'),
]


