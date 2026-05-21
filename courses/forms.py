import random
from django import forms
from .models import Course, CourseApplication


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'start_date', 'end_date',
                  'max_participants', 'price', 'status']
        widgets = {
            'title':            forms.TextInput(attrs={'class': 'form-control'}),
            'description':      forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date':         forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control'}),
            'price':            forms.NumberInput(attrs={'class': 'form-control',
                                                         'step': '0.01', 'min': '0'}),
            'status':           forms.Select(attrs={'class': 'form-select'}),
        }


def _make_captcha():
    """Return (question_str, answer_int) for a simple maths captcha."""
    a = random.randint(2, 12)
    b = random.randint(2, 12)
    op = random.choice(['+', '×'])
    if op == '+':
        return f'{a} + {b}', a + b
    else:
        return f'{a} × {b}', a * b


class CourseApplicationForm(forms.ModelForm):
    captcha_answer = forms.CharField(
        label='',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your answer',
            'autocomplete': 'off',
            'style': 'max-width:140px;',
        }),
    )

    class Meta:
        model = CourseApplication
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'experience']
        widgets = {
            'first_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'email':       forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':       forms.TextInput(attrs={'class': 'form-control'}),
            'address':     forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, captcha_answer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._captcha_answer = captcha_answer

    def clean_captcha_answer(self):
        given = self.cleaned_data.get('captcha_answer', '').strip()
        try:
            if int(given) != self._captcha_answer:
                raise forms.ValidationError('Incorrect answer — please try again.')
        except (ValueError, TypeError):
            raise forms.ValidationError('Please enter a number.')
        return given


class ApplicantDetailForm(forms.ModelForm):
    """Filled by the applicant via the token link in their acceptance email."""
    class Meta:
        model = CourseApplication
        fields = ['date_of_birth', 'eye_dominance', 'handedness', 'strength']
        widgets = {
            'date_of_birth':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'eye_dominance':  forms.Select(attrs={'class': 'form-select'}),
            'handedness':     forms.Select(attrs={'class': 'form-select'}),
            'strength':       forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'date_of_birth':  'Date of Birth',
            'eye_dominance':  'Eye Dominance (which eye do you close when aiming?)',
            'handedness':     'Draw Hand (which hand pulls the bowstring?)',
            'strength':       'Physical Strength / Fitness Level',
        }
