from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Topic, Post
from .forms import TopicForm, PostForm


@login_required
def topic_list(request):
    topics = Topic.objects.all().select_related('created_by').prefetch_related('posts')
    return render(request, 'forum/topic_list.html', {'topics': topics})


@login_required
def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    posts = topic.posts.select_related('author', 'author__profile').order_by('created_at')
    form = None
    if not topic.is_closed and request.user.is_member:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.topic = topic
                post.author = request.user
                post.save()
                messages.success(request, 'Reply posted.')
                return redirect('topic_detail', pk=pk)
        else:
            form = PostForm()
    return render(request, 'forum/topic_detail.html', {'topic': topic, 'posts': posts, 'form': form})


@login_required
def topic_create(request):
    if not request.user.is_member:
        messages.error(request, 'Only members can create topics.')
        return redirect('topic_list')
    if request.method == 'POST':
        form = TopicForm(request.POST)
        post_form = PostForm(request.POST, request.FILES)
        if form.is_valid() and post_form.is_valid():
            topic = form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            post = post_form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()
            messages.success(request, 'Topic created.')
            return redirect('topic_detail', pk=topic.pk)
    else:
        form = TopicForm()
        post_form = PostForm()
    return render(request, 'forum/topic_form.html', {'form': form, 'post_form': post_form})
