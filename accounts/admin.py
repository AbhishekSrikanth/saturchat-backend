from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'is_staff', 'is_online', 'is_bot')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('bio', 'avatar', 'is_online', 'last_activity')}),
        ('API Keys', {'fields': ('openai_api_key', 'anthropic_api_key')}),
        ('Bot Flags', {'fields': ('is_bot',)}),
    )
