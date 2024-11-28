from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import (
    MinLengthValidator, 
    MaxLengthValidator, 
)
from datetime import timedelta

class Habit(models.Model):
    """
    Model representing a user's habit to track
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom')
    ]

    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]

    # Relationships
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='habits'
    )

    # Basic Habit Information
    name = models.CharField(
        max_length=100, 
        validators=[
            MinLengthValidator(3, "Habit name must be at least 3 characters long"),
            MaxLengthValidator(100, "Habit name cannot exceed 100 characters")
        ]
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        max_length=500
    )

    # Tracking Parameters
    frequency = models.CharField(
        max_length=10, 
        choices=FREQUENCY_CHOICES, 
        default='daily'
    )
    difficulty = models.CharField(
        max_length=10, 
        choices=DIFFICULTY_LEVELS, 
        default='medium'
    )

    start_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['-created_at']
        verbose_name_plural = 'Habits'

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def calculate_current_streak(self):
        """
        Calculate the current streak for the habit (Future implementation)
        """
        completed_logs = self.progress_set.filter(
            status=ProgressLog.STATUS_CHOICES[0][0]  # Completed
        ).order_by('-date')
        
        current_streak = 0
        today = timezone.now().date()

        for log in completed_logs:
            if log.date == today - timedelta(days=current_streak):
                current_streak += 1
            else:
                break
        
        return current_streak

    def calculate_completion_percentage(self, days=30):
        """
        Calculate habit completion percentage for given period (Future 
        implementation)
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        total_logs = self.progress_set.filter(
            date__range=[start_date, end_date]
        ).count()
        
        completed_logs = self.progress_set.filter(
            date__range=[start_date, end_date],
            status=ProgressLog.STATUS_CHOICES[0][0]  # Completed
        ).count()
        
        return (completed_logs / total_logs * 100) if total_logs > 0 else 0

class ProgressLog(models.Model):
    """
    Model to track daily progress for each habit
    """
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('missed', 'Missed')
    ]

    habit = models.ForeignKey(
        Habit, 
        on_delete=models.CASCADE, 
        related_name='progress_set'
    )
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='missed'
    )
    notes = models.TextField(
        blank=True, 
        null=True, 
        max_length=300
    )

    # Track minutes for future features
    duration_minutes = models.PositiveIntegerField(
        null=True, 
        blank=True
    )

    class Meta:
        unique_together = ('habit', 'date')
        ordering = ['-date']
        verbose_name_plural = 'Progress Logs'

    def __str__(self):
        return f"{self.habit.name} - {self.date} - {self.status}"

    @classmethod
    def log_progress(cls, habit, status, date=None, notes=None, duration=None):
        """
        Convenience method to log habit progress
        """
        if date is None:
            date = timezone.now().date()
        
        progress_log, created = cls.objects.get_or_create(
            habit=habit,
            date=date,
            defaults={
                'status': status,
                'notes': notes,
                'duration_minutes': duration
            }
        )
        
        if not created:
            progress_log.status = status
            progress_log.notes = notes
            progress_log.duration_minutes = duration
            progress_log.save()
        
        return progress_log