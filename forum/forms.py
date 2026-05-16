from django import forms
from .models import Topic, Post


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title']
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Topic title...'})}


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['body', 'image']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your post...'}),
        }
