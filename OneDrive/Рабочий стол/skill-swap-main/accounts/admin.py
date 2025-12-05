from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Skill, ExchangeRequest


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "full_name", "university", "avatar")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "role",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email", "full_name", "university", "avatar", "role"),
            },
        ),
    )
    list_display = ("username", "email", "full_name", "university", "points", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "full_name", "university")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "skill", "status", "sender_confirmed", "receiver_confirmed", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("sender__username", "receiver__username", "skill__name")

# Register your models here.
