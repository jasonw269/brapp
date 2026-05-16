from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Profile


class BRAppUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'committee_role')


class BRAppUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = BRAppUserChangeForm
    add_form = BRAppUserCreationForm

    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'committee_role', 'is_active']
    list_filter = ['role', 'committee_role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    # Explicitly defined — no tuple concatenation with BaseUserAdmin
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('BRApp Roles', {'fields': ('role', 'committee_role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name',
                       'password1', 'password2', 'role', 'committee_role'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'registration_number', 'gender', 'date_of_birth']
    search_fields = ['full_name', 'registration_number', 'user__username', 'user__email']
    raw_id_fields = ['user']
