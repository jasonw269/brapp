import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Course(models.Model):
    STATUS_OPEN   = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        ('open',   'Open for Applications'),
        ('closed', 'Closed'),
    ]

    title            = models.CharField(max_length=200)
    description      = models.TextField()
    start_date       = models.DateField()
    end_date         = models.DateField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(default=10)
    price            = models.DecimalField(max_digits=8, decimal_places=2, default=0.00,
                                           help_text='Course fee in GBP (0 = free)')
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_by       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                         null=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def confirmed_count(self):
        return self.applications.filter(status='confirmed').count()

    @property
    def spaces_remaining(self):
        return max(0, self.max_participants - self.confirmed_count)

    @property
    def is_full(self):
        return self.spaces_remaining == 0


class CourseApplication(models.Model):
    STATUS_PENDING   = 'pending'
    STATUS_WAITLIST  = 'waitlist'
    STATUS_ACCEPTED  = 'accepted'    # Accepted — awaiting details + payment
    STATUS_DETAILS   = 'details'     # Details submitted — awaiting payment confirmation
    STATUS_CONFIRMED = 'confirmed'   # Paid and confirmed — on the course
    STATUS_REJECTED  = 'rejected'
    STATUS_CHOICES = [
        ('pending',   'Pending Review'),
        ('waitlist',  'On Waitlist'),
        ('accepted',  'Accepted — Awaiting Details'),
        ('details',   'Details Submitted — Awaiting Payment'),
        ('confirmed', 'Confirmed'),
        ('rejected',  'Rejected'),
    ]

    EYE_LEFT   = 'left'
    EYE_RIGHT  = 'right'
    EYE_BOTH   = 'both'
    EYE_UNKNOWN = 'unknown'
    EYE_CHOICES = [
        ('left',    'Left'),
        ('right',   'Right'),
        ('both',    'Both / Central'),
        ('unknown', 'Not sure'),
    ]

    HAND_LEFT  = 'left'
    HAND_RIGHT = 'right'
    HAND_CHOICES = [
        ('left',  'Left'),
        ('right', 'Right'),
    ]

    STRENGTH_LOW  = 'low'
    STRENGTH_MED  = 'medium'
    STRENGTH_HIGH = 'high'
    STRENGTH_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]

    # Core details
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='applications')
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    email       = models.EmailField()
    phone       = models.CharField(max_length=20, blank=True)
    address     = models.TextField(blank=True)
    experience  = models.TextField(blank=True, help_text='Any previous archery experience?')
    status      = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='course_applications')
    applied_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    admin_notes = models.TextField(blank=True)

    # Acceptance token (UUID sent in email link)
    acceptance_token      = models.UUIDField(unique=True, editable=False, null=True, blank=True)
    acceptance_email_sent = models.DateTimeField(null=True, blank=True)

    # Applicant detail form (filled via token link)
    date_of_birth  = models.DateField(null=True, blank=True)
    eye_dominance  = models.CharField(max_length=10, choices=EYE_CHOICES, blank=True)
    handedness     = models.CharField(max_length=10, choices=HAND_CHOICES, blank=True)
    strength       = models.CharField(max_length=10, choices=STRENGTH_CHOICES, blank=True)
    details_submitted_at = models.DateTimeField(null=True, blank=True)

    # Payment
    payment_confirmed    = models.BooleanField(default=False)
    payment_confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                              null=True, blank=True,
                                              related_name='payment_confirmations')
    payment_confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} — {self.course}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def details_complete(self):
        return bool(self.date_of_birth and self.eye_dominance and
                    self.handedness and self.strength)
