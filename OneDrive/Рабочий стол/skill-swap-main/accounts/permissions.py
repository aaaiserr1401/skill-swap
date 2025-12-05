"""
Custom permissions for SkillSwap
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение: только администраторы могут изменять,
    остальные могут только читать
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_admin_user() or request.user.is_staff
        )


class IsModeratorOrReadOnly(permissions.BasePermission):
    """
    Разрешение: модераторы и администраторы могут изменять,
    остальные могут только читать
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_moderator()


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Разрешение: владелец объекта или модератор могут изменять
    """
    def has_object_permission(self, request, view, obj):
        # Модераторы могут все
        if request.user.is_moderator():
            return True
        
        # Владелец может изменять свой объект
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'sender'):
            return obj.sender == request.user
        
        return False

