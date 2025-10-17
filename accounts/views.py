from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator
from .models import ExchangeRequest, User
from .forms import RegisterForm, LoginForm, ProfileForm, ExchangeCreateForm, ExchangeSendForm


class UserLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'accounts/login.html'


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            # M2M fields saved by ModelForm when commit=True
            return redirect('home')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def profile_detail(request):
    # Skeleton history: last 10 exchanges related to the user
    recent_exchanges = ExchangeRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver', 'skill')[:10]
    return render(request, 'accounts/profile_detail.html', {
        'user_obj': request.user,
        'recent_exchanges': recent_exchanges,
    })


@login_required
def exchange_list(request):
    items = ExchangeRequest.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).select_related('sender', 'receiver', 'skill')
    return render(request, 'exchanges/list.html', { 'items': items })


@login_required
def exchange_create(request):
    if request.method == 'POST':
        form = ExchangeCreateForm(request.POST)
        if form.is_valid():
            ex: ExchangeRequest = form.save(commit=False)
            ex.sender = request.user
            ex.status = ExchangeRequest.STATUS_PENDING
            ex.price = 5
            # atomic hold of points
            with transaction.atomic():
                user_locked = request.user.__class__.objects.select_for_update().get(pk=request.user.pk)
                if user_locked.points < ex.price:
                    form.add_error(None, 'Недостаточно баллов для отправки запроса')
                else:
                    user_locked.points = user_locked.points - ex.price
                    user_locked.points_hold = user_locked.points_hold + ex.price
                    user_locked.save(update_fields=['points', 'points_hold'])
                    ex.save()
                    return redirect('accounts:exchange_list')
    else:
        form = ExchangeCreateForm()
    return render(request, 'exchanges/create.html', { 'form': form })


@login_required
def user_detail(request, user_id: int):
    target = get_object_or_404(request.user.__class__, pk=user_id)
    # Show send-request card
    form = ExchangeSendForm()
    return render(request, 'accounts/user_detail.html', {
        'target': target,
        'form': form,
    })


@login_required
def send_request(request, user_id: int):
    target = get_object_or_404(request.user.__class__, pk=user_id)
    if request.method == 'POST':
        form = ExchangeSendForm(request.POST)
        if form.is_valid():
            ex: ExchangeRequest = form.save(commit=False)
            ex.sender = request.user
            ex.receiver = target
            ex.price = 5  # Fixed price for request
            # atomic hold of points
            with transaction.atomic():
                user_locked = request.user.__class__.objects.select_for_update().get(pk=request.user.pk)
                if user_locked.points < ex.price:
                    form.add_error(None, 'Недостаточно баллов')
                else:
                    user_locked.points = user_locked.points - ex.price
                    user_locked.points_hold = user_locked.points_hold + ex.price
                    user_locked.save(update_fields=['points', 'points_hold'])
                    ex.status = ExchangeRequest.STATUS_PENDING
                    ex.save()
                    return redirect('accounts:exchange_list')
    else:
        form = ExchangeSendForm()
    return render(request, 'accounts/user_detail.html', {
        'target': target,
        'form': form,
    })


@login_required
def exchange_accept(request, pk: int):
    if request.method == 'POST':
        ex = get_object_or_404(ExchangeRequest, pk=pk, receiver=request.user)
        ex.status = ExchangeRequest.STATUS_ACCEPTED
        ex.save(update_fields=['status'])
    return redirect('accounts:exchange_list')


@login_required
def exchange_decline(request, pk: int):
    if request.method == 'POST':
        ex = get_object_or_404(ExchangeRequest, pk=pk, receiver=request.user)
        # refund hold to sender
        with transaction.atomic():
            sender_locked = ex.sender.__class__.objects.select_for_update().get(pk=ex.sender_id)
            sender_locked.points_hold = sender_locked.points_hold - ex.price
            sender_locked.points = sender_locked.points + ex.price
            sender_locked.save(update_fields=['points_hold', 'points'])
            ex.status = ExchangeRequest.STATUS_DECLINED
            ex.save(update_fields=['status'])
    return redirect('accounts:exchange_list')


@login_required
def inbox_requests(request):
    # Incoming are those where current user is receiver and status is pending
    incoming = ExchangeRequest.objects.filter(receiver=request.user, status=ExchangeRequest.STATUS_PENDING).select_related('sender', 'skill')
    return render(request, 'exchanges/inbox.html', { 'incoming': incoming })


@login_required
def exchange_confirm(request, pk: int):
    if request.method == 'POST':
        ex = get_object_or_404(ExchangeRequest, pk=pk)
        if ex.sender == request.user:
            ex.sender_confirmed = True
            from django.utils import timezone
            ex.sender_confirmed_at = timezone.now()
        if ex.receiver == request.user:
            ex.receiver_confirmed = True
            from django.utils import timezone
            ex.receiver_confirmed_at = timezone.now()
        ex.save(update_fields=['sender_confirmed', 'receiver_confirmed', 'sender_confirmed_at', 'receiver_confirmed_at'])
        ex.try_complete()
    return redirect('accounts:exchange_list')


@login_required
def exchange_detail(request, pk: int):
    ex = get_object_or_404(ExchangeRequest.objects.select_related('sender', 'receiver', 'skill'), pk=pk)
    return render(request, 'exchanges/detail.html', { 'ex': ex })


@login_required
def user_search(request):
    search_query = request.GET.get('q', '')
    users = User.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Exclude current user from results
    users = users.exclude(id=request.user.id).order_by('username')
    
    # Pagination
    paginator = Paginator(users, 12)  # 12 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/user_search.html', {
        'users': page_obj,
        'search_query': search_query,
    })
