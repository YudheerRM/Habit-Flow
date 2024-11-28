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
    Represents a habit that a user wants to track and maintain.

    This model allows users to define and monitor their personal habits, 
    including frequency, difficulty level, and tracking progress.

    Attributes:
        FREQUENCY_CHOICES (list): Predefined choices for habit tracking frequency.
        DIFFICULTY_LEVELS (list): Predefined difficulty levels for habits.
        user (ForeignKey): The user who owns the habit.
        name (CharField): The name of the habit, with length constraints.
        description (TextField, optional): Additional details about the habit.
        frequency (CharField): How often the habit should be performed.
        difficulty (CharField): Subjective difficulty level of the habit.
        start_date (DateField): The date the user began tracking the habit.
        is_active (BooleanField): Whether the habit is currently being tracked.
        created_at (DateTimeField): Timestamp of habit creation.
        updated_at (DateTimeField): Timestamp of last update.

    Meta:
        - Ensures unique habit names per user
        - Orders habits by creation date (most recent first)
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
        Calculate the current consecutive days the habit has been completed.

        This method examines the habit's progress logs to determine the current 
        streak by counting consecutive completed days from today backward.

        Returns:
            int: Number of consecutive days the habit has been completed.
        
        Note:
            - Assumes completed logs are ordered from most recent to oldest
            - Stops counting streak when a non-consecutive day is encountered
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
        Calculate the percentage of habit completion for a given time period.

        Args:
            days (int, optional): Number of days to calculate completion over. 
                                  Defaults to 30 days.

        Returns:
            float: Percentage of habit completion (0-100).
                   Returns 0 if no logs exist in the specified period.

        Note:
            - Considers only logs within the specified date range
            - Calculates based on completed vs. total logs
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
    Tracks daily progress for individual habits.

    This model allows logging the status of a habit on a specific date, 
    including completion status, optional notes, and time spent.

    Attributes:
        STATUS_CHOICES (list): Predefined status options for habit tracking.
        habit (ForeignKey): The habit being logged.
        date (DateField): The date of the log entry.
        status (CharField): Current status of the habit (completed/skipped/missed).
        notes (TextField, optional): Additional comments about the habit performance.
        duration_minutes (PositiveIntegerField, optional): Time spent on the habit.

    Meta:
        - Ensures unique log per habit per date
        - Orders logs by most recent date
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
        """
        String representation of the ProgressLog instance.

        Returns:
            str: A string combining habit name, date, and status.
        """
        return f"{self.habit.name} - {self.date} - {self.status}"

    @classmethod
    def log_progress(cls, habit, status, date=None, notes=None, duration=None):
        """
        Convenience method to create or update a habit progress log.

        This method allows easy logging of habit progress, either creating 
        a new log or updating an existing one for a specific date.

        Args:
            habit (Habit): The habit being logged.
            status (str): Status of the habit (completed/skipped/missed).
            date (date, optional): Date of the log. Defaults to current date.
            notes (str, optional): Additional notes about the habit performance.
            duration (int, optional): Time spent on the habit in minutes.

        Returns:
            ProgressLog: The created or updated progress log instance.

        Note:
            - If a log for the given habit and date exists, it will be updated
            - If no log exists, a new one will be created
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