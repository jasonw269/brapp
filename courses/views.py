from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, CourseApplication
from .forms import CourseForm, CourseApplicationForm


def course_list(request):
    courses = Course.objects.filter(status='open').order_by('start_date')
    return render(request, 'courses/list.html', {'courses': courses})


def course_apply(request, pk):
    course = get_object_or_404(Course, pk=pk, status='open')
    if request.method == 'POST':
        form = CourseApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.course = course
            if request.user.is_authenticated and request.user.role == 'course_guest':
                app.user = request.user
            app.save()
            messages.success(request, 'Your application has been submitted. We will be in touch soon.')
            return redirect('course_applied')
    else:
        form = CourseApplicationForm()
    return render(request, 'courses/apply.html', {'course': course, 'form': form})


def course_applied(request):
    return render(request, 'courses/applied.html')


@login_required
def course_manage(request):
    if not (request.user.is_committee or request.user.is_admin):
        messages.error(request, 'Access denied.')
        return redirect('course_list')
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'courses/manage.html', {'courses': courses})


@login_required
def course_create(request):
    if not (request.user.is_committee or request.user.is_admin):
        messages.error(request, 'Access denied.')
        return redirect('course_list')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()
            messages.success(request, 'Course created.')
            return redirect('course_manage')
    else:
        form = CourseForm()
    return render(request, 'courses/form.html', {'form': form, 'action': 'Create'})


@login_required
def course_applications(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not (request.user.is_committee or request.user.is_admin):
        messages.error(request, 'Access denied.')
        return redirect('course_list')
    applications = course.applications.order_by('applied_at')
    return render(request, 'courses/applications.html', {'course': course, 'applications': applications})


@login_required
def application_update(request, pk):
    app = get_object_or_404(CourseApplication, pk=pk)
    if not (request.user.is_committee or request.user.is_admin):
        messages.error(request, 'Access denied.')
        return redirect('course_list')
    new_status = request.POST.get('status')
    if new_status in ['pending', 'waitlist', 'accepted', 'rejected']:
        app.status = new_status
        app.admin_notes = request.POST.get('admin_notes', app.admin_notes)
        app.save()
        messages.success(request, f'Application status updated to {new_status}.')
    return redirect('course_applications', pk=app.course.pk)
