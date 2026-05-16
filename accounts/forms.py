from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Profile


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'full_name', 'address_line1', 'address_line2', 'town', 'county', 'postcode', 'gender', 'date_of_birth', 'bio']
        widgets = {
            'full_name':     forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'town':          forms.TextInput(attrs={'class': 'form-control'}),
            'county':        forms.TextInput(attrs={'class': 'form-control'}),
            'postcode':      forms.TextInput(attrs={'class': 'form-control'}),
            'gender':        forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bio':           forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class UserRoleForm(forms.ModelForm):
    """Admin-only form to set a user's role, committee role and basic account fields."""

    COMMITTEE_CHOICES_WITH_BLANK = [('', '— None —')] + User.COMMITTEE_CHOICES

    committee_role = forms.ChoiceField(
        choices=COMMITTEE_CHOICES_WITH_BLANK,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Committee role',
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'committee_role', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'role':       forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_committee_role(self):
        return self.cleaned_data['committee_role'] or None
