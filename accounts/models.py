from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_MEMBER = 'member'
    ROLE_GUEST = 'guest'
    ROLE_COURSE_GUEST = 'course_guest'

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('guest', 'Guest'),
        ('course_guest', 'Course Guest'),
    ]

    COMMITTEE_CHOICES = [
        ('Treasurer', 'Treasurer'),
        ('Chair', 'Chair'),
        ('Secretary', 'Secretary'),
        ('Equipment', 'Equipment Officer'),
        ('Records', 'Records Officer'),
        ('Member', 'Member'),
        ('Beginners', 'Beginners Officer'),
        ('Social', 'Social Secretary'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')
    committee_role = models.CharField(max_length=20, choices=COMMITTEE_CHOICES, blank=True, null=True)

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_member(self):
        return self.role in ('member', 'admin') or self.is_superuser

    @property
    def is_committee(self):
        return self.committee_role is not None and self.is_member

    @property
    def is_records_or_admin(self):
        return self.is_admin or self.committee_role == 'Records'

    def __str__(self):
        return self.get_full_name() or self.username


class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    full_name = models.CharField(max_length=200)
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    registration_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    date_joined_club = models.DateField(blank=True, null=True, verbose_name='Original date of joining')
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.full_name}"
