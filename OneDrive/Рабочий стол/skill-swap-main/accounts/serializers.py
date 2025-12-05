from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Skill, ExchangeRequest

User = get_user_model()


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'slug', 'description', 'photo', 'experience_years']


class UserSerializer(serializers.ModelSerializer):
    skills_can_teach = SkillSerializer(many=True, read_only=True)
    skills_to_learn = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'university', 
            'avatar', 'points', 'skills_can_teach', 'skills_to_learn',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'points']


class UserListSerializer(serializers.ModelSerializer):
    """Simplified user serializer for list views"""
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'university', 'avatar', 'points']


class ExchangeRequestSerializer(serializers.ModelSerializer):
    sender = UserListSerializer(read_only=True)
    receiver = UserListSerializer(read_only=True)
    skill = SkillSerializer(read_only=True)
    
    class Meta:
        model = ExchangeRequest
        fields = [
            'id', 'sender', 'receiver', 'skill', 'message', 'price',
            'status', 'sender_confirmed', 'receiver_confirmed',
            'sender_confirmed_at', 'receiver_confirmed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'sender_confirmed_at', 'receiver_confirmed_at']


class ExchangeRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRequest
        fields = ['receiver', 'skill', 'message', 'price']


class ExchangeRequestActionSerializer(serializers.Serializer):
    """Serializer for accept/decline/confirm actions"""
    action = serializers.ChoiceField(choices=['accept', 'decline', 'confirm'])
    
    def validate_action(self, value):
        if value not in ['accept', 'decline', 'confirm']:
            raise serializers.ValidationError("Invalid action")
        return value
