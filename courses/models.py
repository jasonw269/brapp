from django.db import models
from django.conf import settings


class Course(models.Model):
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        ('open', 'Open for Applications'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(default=10)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text='Course fee in GBP (0 = free)')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CourseApplication(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_WAITLIST = 'waitlist'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('waitlist', 'On Waitlist'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='applications')
    # Non-member details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    experience = models.TextField(blank=True, help_text="Any previous archery experience?")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='course_applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.course}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
