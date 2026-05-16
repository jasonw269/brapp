from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'committee_role', 'is_active']
    list_filter = ['role', 'committee_role', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('BRApp', {'fields': ('role', 'committee_role')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('BRApp', {'fields': ('role', 'committee_role')}),
    )
