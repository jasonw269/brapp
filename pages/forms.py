from django import forms
from .models import GalleryImage, SiteContent


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['title', 'description', 'image', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AboutForm(forms.Form):
    hero_tagline = forms.CharField(
        label='Hero tagline',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    card1_title = forms.CharField(
        label='Feature 1 title',
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    card1_body = forms.CharField(
        label='Feature 1 text',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    card2_title = forms.CharField(
        label='Feature 2 title',
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    card2_body = forms.CharField(
        label='Feature 2 text',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    card3_title = forms.CharField(
        label='Feature 3 title',
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    card3_body = forms.CharField(
        label='Feature 3 text',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    who_we_are_left = forms.CharField(
        label='"Who We Are" left column',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    who_we_are_right_intro = forms.CharField(
        label='"Who We Are" right intro',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    meeting_nights = forms.CharField(
        label='Meeting nights',
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    weekend_sessions = forms.CharField(
        label='Weekend sessions',
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    cta_body = forms.CharField(
        label='Call-to-action text',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))


class ContactContentForm(forms.Form):
    address_line1 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    address_line2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address_line3 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    social_handle = forms.CharField(
        label='Social media handle',
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    tuesday_hours = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    thursday_hours = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    sunday_hours = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    maps_url = forms.URLField(
        label='Google Maps URL', required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'}))
