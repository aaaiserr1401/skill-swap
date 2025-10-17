from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import ExchangeRequest
from .forms import RegisterForm, LoginForm, ProfileForm, ExchangeCreateForm


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
            ex.save()
            return redirect('exchange_list')
    else:
        form = ExchangeCreateForm()
    return render(request, 'exchanges/create.html', { 'form': form })


@login_required
def exchange_accept(request, pk: int):
    if request.method == 'POST':
        ex = get_object_or_404(ExchangeRequest, pk=pk, receiver=request.user)
        ex.status = ExchangeRequest.STATUS_ACCEPTED
        ex.save(update_fields=['status'])
    return redirect('exchange_list')


@login_required
def exchange_decline(request, pk: int):
    if request.method == 'POST':
        ex = get_object_or_404(ExchangeRequest, pk=pk, receiver=request.user)
        ex.status = ExchangeRequest.STATUS_DECLINED
        ex.save(update_fields=['status'])
    return redirect('exchange_list')


@login_required
def exchange_confirm(request, pk: int):
    if request.method == 'POST':
        ex = get_object_or_404(ExchangeRequest, pk=pk)
        if ex.sender == request.user:
            ex.sender_confirmed = True
        if ex.receiver == request.user:
            ex.receiver_confirmed = True
        ex.save(update_fields=['sender_confirmed', 'receiver_confirmed'])
        ex.try_complete()
    return redirect('exchange_list')

# Create your views here.
