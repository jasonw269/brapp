from django.db import models
from django.conf import settings


class Round(models.Model):
    METRIC = 'metric'
    IMPERIAL = 'imperial'
    SYSTEM_CHOICES = [
        ('metric', 'Metric'),
        ('imperial', 'Imperial'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    number_of_arrows = models.PositiveIntegerField()
    maximum_score = models.PositiveIntegerField()
    system = models.CharField(max_length=10, choices=SYSTEM_CHOICES, default='metric')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_system_display()})"


class Score(models.Model):
    BOW_RECURVE = 'Recurve'
    BOW_COMPOUND = 'Compound'
    BOW_BAREBOW = 'Barebow'
    BOW_LONGBOW = 'Longbow'
    BOW_OTHER = 'Other'

    BOW_CHOICES = [
        ('Recurve', 'Recurve'),
        ('Compound', 'Compound'),
        ('Barebow', 'Barebow'),
        ('Longbow', 'Longbow'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scores')
    round = models.ForeignKey(Round, on_delete=models.PROTECT)
    date_shot = models.DateField()
    location = models.CharField(max_length=200)
    bow_type = models.CharField(max_length=20, choices=BOW_CHOICES)
    score = models.PositiveIntegerField()
    witness = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    is_personal_best = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_shot']

    def __str__(self):
        return f"{self.user} - {self.round} - {self.score} ({self.bow_type})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_personal_bests()

    def _update_personal_bests(self):
        # Reset all scores for this user/round/bow combination
        Score.objects.filter(
            user=self.user,
            round=self.round,
            bow_type=self.bow_type
        ).update(is_personal_best=False)
        # Mark the highest score as personal best
        best = Score.objects.filter(
            user=self.user,
            round=self.round,
            bow_type=self.bow_type
        ).order_by('-score').first()
        if best:
            Score.objects.filter(pk=best.pk).update(is_personal_best=True)
