from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserPreferences


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user preferences."""
    
    class Meta:
        model = UserPreferences
        exclude = ['id', 'user']
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - used for profile display."""
    
    preferences = UserPreferencesSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'profile_picture', 'bio',
            'timezone', 'language', 'theme',
            'email_notifications', 'push_notifications',
            'is_premium', 'premium_expires_at',
            'created_at', 'updated_at', 'last_active',
            'preferences'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_active', 'is_premium', 'premium_expires_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create user and associated preferences."""
        # Remove password_confirm from validated data
        validated_data.pop('password_confirm')
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Create default preferences for the user
        UserPreferences.objects.create(user=user)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'date_of_birth', 'profile_picture', 'bio',
            'timezone', 'language', 'theme',
            'email_notifications', 'push_notifications'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs