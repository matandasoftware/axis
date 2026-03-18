from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserPreferences


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with additional fields."""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_premium', 'created_at']
    list_filter = ['is_premium', 'is_staff', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    
    # Add custom fields to the admin form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Personal Info', {
            'fields': ('phone_number', 'date_of_birth', 'profile_picture', 'bio')
        }),
        ('Preferences', {
            'fields': ('timezone', 'language', 'theme')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'push_notifications')
        }),
        ('Premium', {
            'fields': ('is_premium', 'premium_expires_at')
        }),
        ('Timestamps', {
            'fields': ('last_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_active']


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """Admin for user preferences."""
    
    list_display = ['user', 'fitness_level', 'default_currency', 'created_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['fitness_level', 'default_currency', 'default_travel_mode']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Work Preferences', {
            'fields': ('default_work_start_time', 'default_work_end_time', 'work_days')
        }),
        ('Task Preferences', {
            'fields': ('default_task_duration', 'task_reminder_minutes')
        }),
        ('Workout Preferences', {
            'fields': ('fitness_level', 'workout_reminder_enabled')
        }),
        ('Finance Preferences', {
            'fields': ('default_currency', 'monthly_budget')
        }),
        ('Travel Preferences', {
            'fields': ('default_travel_mode',)
        }),
        ('Privacy', {
            'fields': ('share_activity_data',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
