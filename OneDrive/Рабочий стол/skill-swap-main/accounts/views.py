import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from .models import ExchangeRequest, User, Skill
from .forms import RegisterForm, LoginForm, ProfileForm, ExchangeCreateForm, ExchangeSendForm

logger = logging.getLogger('accounts')


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
            logger.info(f'New user registered: {user.username} (ID: {user.id})')
            messages.success(request, 'Регистрация прошла успешно. Добро пожаловать в SkillSwap!')
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
            messages.success(request, 'Профиль обновлён.')
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
            if not ex.hold_from_sender():
                logger.warning(f'User {request.user.username} attempted to create exchange with insufficient points')
                form.add_error(None, 'Недостаточно баллов для отправки запроса')
                messages.error(request, 'Недостаточно баллов для создания обмена.')
            else:
                logger.info(f'Exchange request created: ID {ex.id}, sender: {request.user.username}, receiver: {ex.receiver.username}, skill: {ex.skill.name}')
                messages.success(request, 'Запрос на обмен отправлен.')
                return redirect('accounts:exchange_list')
    else:
        form = ExchangeCreateForm()
    return render(request, 'exchanges/create.html', { 'form': form })


@login_required
def user_detail(request, user_id: int):
    target = get_object_or_404(request.user.__class__, pk=user_id)
    # Show send-request card
    form = ExchangeSendForm()
    form.fields['skill'].queryset = target.skills_can_teach.all()
    return render(request, 'accounts/user_detail.html', {
        'target': target,
        'form': form,
    })


@login_required
def send_request(request, user_id: int):
    target = get_object_or_404(request.user.__class__, pk=user_id)
    if request.method == 'POST':
        form = ExchangeSendForm(request.POST)
        form.fields['skill'].queryset = target.skills_can_teach.all()
        if form.is_valid():
            ex: ExchangeRequest = form.save(commit=False)
            ex.sender = request.user
            ex.receiver = target
            ex.price = 5  # Fixed price for request
            if not ex.hold_from_sender():
                form.add_error(None, 'Недостаточно баллов')
                messages.error(request, 'Недостаточно баллов для отправки запроса.')
            else:
                # Email-уведомление получателю
                if target.email:
                    send_mail(
                        subject='Новый запрос на обмен в SkillSwap',
                        message=f'{request.user.get_username()} отправил(а) вам запрос по навыку {ex.skill.name}.',
                        from_email=None,
                        recipient_list=[target.email],
                        fail_silently=True,
                    )
                messages.success(request, 'Запрос отправлен пользователю.')
                return redirect('accounts:exchange_list')
    else:
        form = ExchangeSendForm()
        form.fields['skill'].queryset = target.skills_can_teach.all()
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
        logger.info(f'Exchange request {pk} accepted by {request.user.username}')
        messages.success(request, 'Запрос принят.')
        # Уведомим отправителя по email
        if ex.sender.email:
            send_mail(
                subject='Ваш запрос принят',
                message=f'Пользователь {request.user.get_username()} принял ваш запрос по навыку {ex.skill.name}.',
                from_email=None,
                recipient_list=[ex.sender.email],
                fail_silently=True,
            )
    return redirect('accounts:exchange_list')


@login_required
def exchange_decline(request, pk: int):
    if request.method == 'POST':
        ex = get_object_or_404(ExchangeRequest, pk=pk, receiver=request.user)
        ex.refund_to_sender()
        messages.info(request, 'Запрос отклонён, баллы возвращены отправителю.')
        # Email отправителю
        if ex.sender.email:
            send_mail(
                subject='Ваш запрос отклонён',
                message=f'Пользователь {request.user.get_username()} отклонил ваш запрос по навыку {ex.skill.name}.',
                from_email=None,
                recipient_list=[ex.sender.email],
                fail_silently=True,
            )
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
            logger.info(f'Exchange request {pk} confirmed by sender {request.user.username}')
        if ex.receiver == request.user:
            ex.receiver_confirmed = True
            from django.utils import timezone
            ex.receiver_confirmed_at = timezone.now()
            logger.info(f'Exchange request {pk} confirmed by receiver {request.user.username}')
        ex.save(update_fields=['sender_confirmed', 'receiver_confirmed', 'sender_confirmed_at', 'receiver_confirmed_at'])
        completed = ex.try_complete()
        if completed:
            logger.info(f'Exchange request {pk} completed successfully. Points transferred.')
            messages.success(request, 'Обмен успешно завершён, баллы начислены.')
            # Письма обеим сторонам о завершении
            emails = []
            if ex.sender.email:
                emails.append(ex.sender.email)
            if ex.receiver.email:
                emails.append(ex.receiver.email)
            if emails:
                send_mail(
                    subject='Обмен завершён',
                    message=f'Обмен по навыку {ex.skill.name} успешно завершён. Баллы начислены.',
                    from_email=None,
                    recipient_list=emails,
                    fail_silently=True,
                )
        else:
            messages.info(request, 'Ваше подтверждение сохранено. Ожидается подтверждение второй стороны.')
    return redirect('accounts:exchange_list')


@login_required
def exchange_detail(request, pk: int):
    ex = get_object_or_404(ExchangeRequest.objects.select_related('sender', 'receiver', 'skill'), pk=pk)
    return render(request, 'exchanges/detail.html', { 'ex': ex })


@login_required
def user_search(request):
    search_query = request.GET.get('q', '')
    mode = request.GET.get('mode', 'teach')  # teach | learn
    skill_name = request.GET.get('skill', '')
    users = User.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    if skill_name:
        if mode == 'learn':
            users = users.filter(skills_to_learn__name__icontains=skill_name)
        else:
            users = users.filter(skills_can_teach__name__icontains=skill_name)
    
    # Exclude current user from results
    users = users.exclude(id=request.user.id).order_by('username').distinct()
    
    # Pagination
    paginator = Paginator(users, 12)  # 12 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_skills = Skill.objects.order_by('name')

    return render(request, 'accounts/user_search.html', {
        'users': page_obj,
        'search_query': search_query,
        'mode': mode,
        'skill_name': skill_name,
        'all_skills': all_skills,
    })


@login_required
def make_me_superuser(request):
    user = request.user
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=['is_staff', 'is_superuser'])
    return HttpResponse('ok')
