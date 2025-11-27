from django.urls import path
from .api_views import (
    UserListAPIView, UserDetailAPIView,
    SkillListAPIView, SkillDetailAPIView,
    ExchangeRequestListAPIView, ExchangeRequestDetailAPIView,
    InboxRequestsAPIView, exchange_action,
    api_login, api_logout
)

app_name = 'api'

urlpatterns = [
    # Authentication
    path('auth/login/', api_login, name='login'),
    path('auth/logout/', api_logout, name='logout'),
    
    # Users
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    
    # Skills
    path('skills/', SkillListAPIView.as_view(), name='skill-list'),
    path('skills/<slug:slug>/', SkillDetailAPIView.as_view(), name='skill-detail'),
    
    # Exchange Requests
    path('exchanges/', ExchangeRequestListAPIView.as_view(), name='exchange-list'),
    path('exchanges/inbox/', InboxRequestsAPIView.as_view(), name='exchange-inbox'),
    path('exchanges/<int:pk>/', ExchangeRequestDetailAPIView.as_view(), name='exchange-detail'),
    path('exchanges/<int:pk>/action/', exchange_action, name='exchange-action'),
]
