from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Skill, ExchangeRequest
from .serializers import (
    UserSerializer, UserListSerializer, SkillSerializer,
    ExchangeRequestSerializer, ExchangeRequestCreateSerializer,
    ExchangeRequestActionSerializer
)

User = get_user_model()


class UserListAPIView(generics.ListAPIView):
    """API endpoint for listing users with search"""
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.exclude(id=self.request.user.id).order_by('username')
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(full_name__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        return queryset


class UserDetailAPIView(generics.RetrieveAPIView):
    """API endpoint for user details"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()


class SkillListAPIView(generics.ListCreateAPIView):
    """API endpoint for listing and creating skills"""
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Skill.objects.all().order_by('name')
    
    def perform_create(self, serializer):
        skill = serializer.save()
        # Assign to current user's skills if requested
        assign_to_teach = self.request.data.get('assign_to_teach', False)
        assign_to_learn = self.request.data.get('assign_to_learn', False)
        
        if assign_to_teach:
            self.request.user.skills_can_teach.add(skill)
        if assign_to_learn:
            self.request.user.skills_to_learn.add(skill)


class SkillDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for skill details"""
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Skill.objects.all()
    lookup_field = 'slug'


class ExchangeRequestListAPIView(generics.ListCreateAPIView):
    """API endpoint for listing and creating exchange requests"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExchangeRequestCreateSerializer
        return ExchangeRequestSerializer
    
    def get_queryset(self):
        # Return requests where user is sender or receiver
        return ExchangeRequest.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        # Set sender to current user
        serializer.save(sender=self.request.user)
        
        # Deduct points atomically
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=self.request.user.pk)
            if user.points < serializer.validated_data['price']:
                raise serializers.ValidationError("Недостаточно баллов")
            
            user.points -= serializer.validated_data['price']
            user.points_hold += serializer.validated_data['price']
            user.save(update_fields=['points', 'points_hold'])


class ExchangeRequestDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for exchange request details"""
    serializer_class = ExchangeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ExchangeRequest.objects.all()
    
    def get_queryset(self):
        # Only allow access to requests where user is sender or receiver
        return ExchangeRequest.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )


class InboxRequestsAPIView(generics.ListAPIView):
    """API endpoint for incoming requests"""
    serializer_class = ExchangeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ExchangeRequest.objects.filter(
            receiver=self.request.user,
            status=ExchangeRequest.STATUS_PENDING
        ).order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def exchange_action(request, pk):
    """API endpoint for exchange actions (accept/decline/confirm)"""
    try:
        exchange = ExchangeRequest.objects.get(pk=pk)
    except ExchangeRequest.DoesNotExist:
        return Response({'error': 'Exchange request not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    if request.user not in [exchange.sender, exchange.receiver]:
        return Response({'error': 'Permission denied'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    serializer = ExchangeRequestActionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    action = serializer.validated_data['action']
    
    if action == 'accept':
        if request.user != exchange.receiver:
            return Response({'error': 'Only receiver can accept'}, 
                           status=status.HTTP_403_FORBIDDEN)
        exchange.status = ExchangeRequest.STATUS_ACCEPTED
        exchange.save()
        
    elif action == 'decline':
        if request.user != exchange.receiver:
            return Response({'error': 'Only receiver can decline'}, 
                           status=status.HTTP_403_FORBIDDEN)
        exchange.status = ExchangeRequest.STATUS_DECLINED
        exchange.save()
        
        # Return points to sender
        with transaction.atomic():
            sender = User.objects.select_for_update().get(pk=exchange.sender.pk)
            sender.points += exchange.price
            sender.points_hold -= exchange.price
            sender.save(update_fields=['points', 'points_hold'])
            
    elif action == 'confirm':
        if request.user == exchange.sender:
            exchange.sender_confirmed = True
            exchange.sender_confirmed_at = timezone.now()
        elif request.user == exchange.receiver:
            exchange.receiver_confirmed = True
            exchange.receiver_confirmed_at = timezone.now()
        else:
            return Response({'error': 'Invalid user'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        exchange.save()
        
        # Try to complete the exchange
        if exchange.try_complete():
            return Response({'message': 'Exchange completed successfully'})
    
    return Response(ExchangeRequestSerializer(exchange).data)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        },
    ),
    responses={
        200: openapi.Response('Success', UserSerializer),
        400: 'Bad Request',
        401: 'Unauthorized',
    },
    tags=['Authentication'],
)
@api_view(['POST'])
def api_login(request):
    """API endpoint for token-based authentication"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    else:
        return Response({'error': 'Invalid credentials'}, 
                       status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_logout(request):
    """API endpoint for logout"""
    try:
        request.user.auth_token.delete()
    except:
        pass
    return Response({'message': 'Logged out successfully'})
