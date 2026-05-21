import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings as django_settings
from .models import Course, CourseApplication
from .forms import CourseForm, CourseApplicationForm, ApplicantDetailForm, _make_captcha

BEGINNERS_ROLES = ('Beginners', 'Chair', 'Secretary')


def _can_manage_courses(user):
    return user.is_admin or user.is_committee


def _can_confirm_payment(user):
    return user.is_admin or user.committee_role in BEGINNERS_ROLES


def course_list(request):
    courses = Course.objects.filter(status='open').order_by('start_date')
    return render(request, 'courses/list.html', {'courses': courses})


def course_apply(request, pk):
    course = get_object_or_404(Course, pk=pk, status='open')

    if course.is_full:
        messages.warning(request, 'This course is full. You will be placed on the waitlist.')

    # Generate captcha and store answer in session
    if request.method == 'GET':
        question, answer = _make_captcha()
        request.session['captcha_answer'] = answer
        request.session['captcha_question'] = question

    question = request.session.get('captcha_question', '? + ?')
    answer   = request.session.get('captcha_answer', 0)

    if request.method == 'POST':
        form = CourseApplicationForm(
            request.POST,
            captcha_answer=request.session.get('captcha_answer', 0),
        )
        if form.is_valid():
            app = form.save(commit=False)
            app.course = course
            # Put on waitlist automatically if course is full
            if course.is_full:
                app.status = CourseApplication.STATUS_WAITLIST
            app.save()
            # Clear captcha from session
            request.session.pop('captcha_answer', None)
            request.session.pop('captcha_question', None)
            return redirect('course_applied')
        else:
            # Regenerate captcha on failure
            question, answer = _make_captcha()
            request.session['captcha_answer'] = answer
            request.session['captcha_question'] = question
    else:
        form = CourseApplicationForm()

    return render(request, 'courses/apply.html', {
        'course': course,
        'form': form,
        'captcha_question': question,
    })


def course_applied(request):
    return render(request, 'courses/applied.html')


# ── Token-based applicant detail form ─────────────────────────────────────────

def applicant_detail_form(request, token):
    """
    Public URL (no login needed) — the applicant fills in their details
    after clicking the link in their acceptance email.
    """
    app = get_object_or_404(CourseApplication, acceptance_token=token)

    if app.status not in ('accepted', 'details'):
        return render(request, 'courses/token_invalid.html', {
            'reason': 'This link is not currently active.'
        })

    already_done = app.details_complete and app.status == 'details'

    if request.method == 'POST' and not already_done:
        form = ApplicantDetailForm(request.POST, instance=app)
        if form.is_valid():
            a = form.save(commit=False)
            a.status = CourseApplication.STATUS_DETAILS
            a.details_submitted_at = timezone.now()
            a.save()
            return redirect('course_details_submitted', token=token)
    else:
        form = ApplicantDetailForm(instance=app)

    return render(request, 'courses/applicant_detail.html', {
        'app': app,
        'form': form,
        'already_done': already_done,
    })


def course_details_submitted(request, token):
    app = get_object_or_404(CourseApplication, acceptance_token=token)
    return render(request, 'courses/details_submitted.html', {'app': app})


# ── Committee views ────────────────────────────────────────────────────────────

@login_required
def course_manage(request):
    if not _can_manage_courses(request.user):
        messages.error(request, 'Access denied.')
        return redirect('course_list')
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'courses/manage.html', {'courses': courses})


@login_required
def course_create(request):
    if not _can_manage_courses(request.user):
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
    if not _can_manage_courses(request.user):
        messages.error(request, 'Access denied.')
        return redirect('course_list')
    applications = course.applications.order_by('applied_at')
    return render(request, 'courses/applications.html', {
        'course': course,
        'applications': applications,
        'can_confirm_payment': _can_confirm_payment(request.user),
    })


@login_required
def application_update(request, pk):
    """Update status and optionally send acceptance email."""
    app = get_object_or_404(CourseApplication, pk=pk)
    if not _can_manage_courses(request.user):
        messages.error(request, 'Access denied.')
        return redirect('course_list')

    new_status = request.POST.get('status')
    valid_statuses = ['pending', 'waitlist', 'accepted', 'rejected']

    if new_status in valid_statuses:
        old_status = app.status
        app.status = new_status
        app.admin_notes = request.POST.get('admin_notes', app.admin_notes)

        # When accepting, generate token and send email
        if new_status == 'accepted' and old_status != 'accepted':
            if not app.acceptance_token:
                app.acceptance_token = uuid.uuid4()
            app.save()
            _send_acceptance_email(request, app)
            messages.success(request, f'Application accepted and email sent to {app.email}.')
        else:
            app.save()
            messages.success(request, f'Application status updated to {new_status}.')

    return redirect('course_applications', pk=app.course.pk)


@login_required
def resend_acceptance_email(request, pk):
    """Resend the acceptance email with the token link."""
    app = get_object_or_404(CourseApplication, pk=pk)
    if not _can_manage_courses(request.user):
        messages.error(request, 'Access denied.')
        return redirect('course_list')
    if not app.acceptance_token:
        app.acceptance_token = uuid.uuid4()
        app.save()
    _send_acceptance_email(request, app)
    messages.success(request, f'Acceptance email resent to {app.email}.')
    return redirect('course_applications', pk=app.course.pk)


@login_required
def confirm_payment(request, pk):
    """Beginners officer / admin confirms payment and finalises the place."""
    app = get_object_or_404(CourseApplication, pk=pk)
    if not _can_confirm_payment(request.user):
        messages.error(request, 'Access denied. Only Beginners Officers, Chair or Secretary can confirm payment.')
        return redirect('course_applications', pk=app.course.pk)

    if app.course.is_full and app.status != 'confirmed':
        messages.error(request, f'Course is full ({app.course.confirmed_count}/{app.course.max_participants} confirmed). Cannot confirm this place.')
        return redirect('course_applications', pk=app.course.pk)

    app.status = CourseApplication.STATUS_CONFIRMED
    app.payment_confirmed = True
    app.payment_confirmed_by = request.user
    app.payment_confirmed_at = timezone.now()
    app.save()

    # Send confirmation email to applicant
    _send_confirmation_email(request, app)
    messages.success(request, f'{app.full_name} confirmed on the course.')
    return redirect('course_applications', pk=app.course.pk)


# ── Email helpers ──────────────────────────────────────────────────────────────

def _build_base_url(request):
    scheme = 'https' if request.is_secure() else 'http'
    return f'{scheme}://{request.get_host()}'


def _send_acceptance_email(request, app):
    base = _build_base_url(request)
    token_url = f"{base}/courses/details/{app.acceptance_token}/"

    subject = f'Your application for {app.course.title} — Next Steps'
    body = render_to_string('courses/emails/acceptance.txt', {
        'app': app,
        'token_url': token_url,
        'base_url': base,
    })

    try:
        send_mail(subject, body, django_settings.DEFAULT_FROM_EMAIL, [app.email])
        app.acceptance_email_sent = timezone.now()
        app.save(update_fields=['acceptance_email_sent'])
    except Exception as e:
        pass  # Logged via console backend in dev


def _send_confirmation_email(request, app):
    base = _build_base_url(request)
    subject = f'You\'re confirmed on {app.course.title}!'
    body = render_to_string('courses/emails/confirmed.txt', {
        'app': app,
        'base_url': base,
    })
    try:
        send_mail(subject, body, django_settings.DEFAULT_FROM_EMAIL, [app.email])
    except Exception:
        pass
