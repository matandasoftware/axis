from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Central to the entire AXIS system - all data links to users.
    """
    # Personal Information
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Profile
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Preferences
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    theme = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='auto'
    )
    
    # Notifications
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    
    # Metadata
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username


class UserPreferences(models.Model):
    """
    Detailed user preferences for customization.
    Separated from User model to keep it clean.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Work Preferences
    default_work_start_time = models.TimeField(default='09:00:00')
    default_work_end_time = models.TimeField(default='17:00:00')
    work_days = models.JSONField(default=list)  # ["Monday", "Tuesday", ...]
    
    # Task Preferences
    default_task_duration = models.IntegerField(default=60)  # minutes
    task_reminder_minutes = models.IntegerField(default=15)
    
    # Workout Preferences
    fitness_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        default='beginner'
    )
    workout_reminder_enabled = models.BooleanField(default=True)
    
    # Finance Preferences
    default_currency = models.CharField(max_length=3, default='USD')
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Travel Preferences
    default_travel_mode = models.CharField(
        max_length=20,
        choices=[
            ('driving', 'Driving'),
            ('walking', 'Walking'),
            ('transit', 'Public Transit'),
            ('cycling', 'Cycling')
        ],
        default='driving'
    )
    
    # Privacy
    share_activity_data = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'
    
    def __str__(self):
        return f"{self.user.username}'s preferences"
