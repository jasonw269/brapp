from django import forms
from .models import Score, Round


class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ['round', 'date_shot', 'location', 'bow_type', 'score', 'witness', 'notes']
        widgets = {
            'round': forms.Select(attrs={'class': 'form-select'}),
            'date_shot': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'bow_type': forms.Select(attrs={'class': 'form-select'}),
            'score': forms.NumberInput(attrs={'class': 'form-control'}),
            'witness': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RoundForm(forms.ModelForm):
    class Meta:
        model = Round
        fields = ['name', 'description', 'number_of_arrows', 'maximum_score', 'system']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'number_of_arrows': forms.NumberInput(attrs={'class': 'form-control'}),
            'maximum_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'system': forms.Select(attrs={'class': 'form-select'}),
        }
