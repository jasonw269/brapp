from django import forms
from .models import Membership, MembershipLevel


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['level', 'start_date', 'end_date', 'price', 'notes']
        widgets = {
            'level': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
