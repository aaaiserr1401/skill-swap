from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('skills/', views.skill_list, name='skill_list'),
    path('skills/<slug:slug>/', views.skill_detail, name='skill_detail'),
]


