from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from .models import User, UserPreferences
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserPreferencesSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]  # Anyone can register
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    API endpoint for user login.
    POST /api/auth/login/
    Body: {"username": "...", "password": "..."}
    Returns: JWT tokens
    """
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """
    API endpoint for user logout.
    POST /api/auth/logout/
    Body: {"refresh": "refresh_token_here"}
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()  # Invalidate the token
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Invalid token or token already blacklisted'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to get and update user profile.
    GET /api/auth/profile/ - Get current user profile
    PUT/PATCH /api/auth/profile/ - Update current user profile
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return full user data with updated info
        return Response(UserSerializer(instance).data)


class ChangePasswordView(APIView):
    """
    API endpoint to change user password.
    POST /api/auth/change-password/
    Body: {"old_password": "...", "new_password": "...", "new_password_confirm": "..."}
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Check old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to get and update user preferences.
    GET /api/auth/preferences/ - Get current user preferences
    PUT/PATCH /api/auth/preferences/ - Update preferences
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPreferencesSerializer
    
    def get_object(self):
        # Get or create preferences for the user
        preferences, created = UserPreferences.objects.get_or_create(user=self.request.user)
        return preferences