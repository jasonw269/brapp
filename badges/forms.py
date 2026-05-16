from django import forms
from .models import Badge


class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AwardBadgeForm(forms.Form):
    badge = forms.ModelChoiceField(queryset=Badge.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
