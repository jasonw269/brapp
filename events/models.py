from django.db import models
from django.conf import settings


class Location(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    TYPE_INTERNAL = 'internal'
    TYPE_EXTERNAL = 'external'
    TYPE_CHOICES = [
        ('internal', 'Internal'),
        ('external', 'External'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    event_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='internal')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title


class EventPollOption(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='poll_options')
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.event.title}: {self.text}"


class EventPollVote(models.Model):
    option = models.ForeignKey(EventPollOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['option', 'user']


class EventAttendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user} attending {self.event}"
