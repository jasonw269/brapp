from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from .models import User, Profile


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'full_name', 'address_line1', 'address_line2',
                  'town', 'county', 'postcode', 'gender', 'date_of_birth', 'bio']
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


COMMITTEE_CHOICES_WITH_BLANK = [('', '— None —')] + User.COMMITTEE_CHOICES


class UserRoleForm(forms.ModelForm):
    """Admin-only: change role, committee role, basic info and active status."""
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


class UserCreateForm(forms.ModelForm):
    """Admin-only: create a new user with password."""
    committee_role = forms.ChoiceField(
        choices=COMMITTEE_CHOICES_WITH_BLANK,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Committee role',
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'committee_role']
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'role':       forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_committee_role(self):
        return self.cleaned_data['committee_role'] or None

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1', '')
        p2 = self.cleaned_data.get('password2', '')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return p2

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password1')
        if password:
            try:
                validate_password(password)
            except forms.ValidationError as e:
                self.add_error('password1', e)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
