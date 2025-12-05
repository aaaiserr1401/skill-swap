"""
Admin panel views for SkillSwap application
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import User, Skill, ExchangeRequest


def is_admin(user):
    """Проверка, является ли пользователь администратором"""
    return user.is_authenticated and user.is_admin_user()


@user_passes_test(is_admin)
def admin_dashboard(request):
    """Главная страница админ-панели"""
    # Статистика пользователей
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    new_users_today = User.objects.filter(
        date_joined__date=timezone.now().date()
    ).count()
    new_users_week = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Статистика навыков
    total_skills = Skill.objects.count()
    popular_skills = Skill.objects.annotate(
        teachers_count=Count('teachers'),
        learners_count=Count('learners')
    ).order_by('-teachers_count')[:5]
    
    # Статистика обменов
    total_exchanges = ExchangeRequest.objects.count()
    pending_exchanges = ExchangeRequest.objects.filter(
        status=ExchangeRequest.STATUS_PENDING
    ).count()
    completed_exchanges = ExchangeRequest.objects.filter(
        status=ExchangeRequest.STATUS_COMPLETED
    ).count()
    
    # Последние обмены
    recent_exchanges = ExchangeRequest.objects.select_related(
        'sender', 'receiver', 'skill'
    ).order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'total_skills': total_skills,
        'popular_skills': popular_skills,
        'total_exchanges': total_exchanges,
        'pending_exchanges': pending_exchanges,
        'completed_exchanges': completed_exchanges,
        'recent_exchanges': recent_exchanges,
    }
    return render(request, 'admin/dashboard.html', context)


@user_passes_test(is_admin)
def admin_users(request):
    """Управление пользователями"""
    search_query = request.GET.get('q', '')
    users = User.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(full_name__icontains=search_query)
        )
    
    paginator = Paginator(users.order_by('-date_joined'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/users.html', {
        'users': page_obj,
        'search_query': search_query,
    })


@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """Детали пользователя"""
    user = get_object_or_404(User, id=user_id)
    sent_exchanges = ExchangeRequest.objects.filter(sender=user).count()
    received_exchanges = ExchangeRequest.objects.filter(receiver=user).count()
    completed_exchanges = ExchangeRequest.objects.filter(
        Q(sender=user) | Q(receiver=user),
        status=ExchangeRequest.STATUS_COMPLETED
    ).count()
    
    return render(request, 'admin/user_detail.html', {
        'user_obj': user,
        'sent_exchanges': sent_exchanges,
        'received_exchanges': received_exchanges,
        'completed_exchanges': completed_exchanges,
    })


@user_passes_test(is_admin)
def admin_skills(request):
    """Управление навыками"""
    search_query = request.GET.get('q', '')
    skills = Skill.objects.annotate(
        teachers_count=Count('teachers'),
        learners_count=Count('learners')
    )
    
    if search_query:
        skills = skills.filter(name__icontains=search_query)
    
    paginator = Paginator(skills.order_by('-teachers_count'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/skills.html', {
        'skills': page_obj,
        'search_query': search_query,
    })


@user_passes_test(is_admin)
def admin_exchanges(request):
    """Управление обменами"""
    status_filter = request.GET.get('status', '')
    exchanges = ExchangeRequest.objects.select_related(
        'sender', 'receiver', 'skill'
    )
    
    if status_filter:
        exchanges = exchanges.filter(status=status_filter)
    
    paginator = Paginator(exchanges.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/exchanges.html', {
        'exchanges': page_obj,
        'status_filter': status_filter,
        'status_choices': ExchangeRequest.STATUS_CHOICES,
    })


@user_passes_test(is_admin)
def admin_exchange_detail(request, exchange_id):
    """Детали обмена"""
    exchange = get_object_or_404(
        ExchangeRequest.objects.select_related('sender', 'receiver', 'skill'),
        id=exchange_id
    )
    
    return render(request, 'admin/exchange_detail.html', {
        'exchange': exchange,
    })

