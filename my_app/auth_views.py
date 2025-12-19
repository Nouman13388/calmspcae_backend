"""
Authentication Views - Registration, Login, Email Verification, Password Reset
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .auth_serializers import (
    RegisterSerializer, LoginSerializer, VerifyEmailSerializer,
    ForgotPasswordSerializer, PasswordResetSerializer, ChangePasswordSerializer,
    UpdateProfileSerializer, UserSerializer, UserDetailSerializer
)
from .email_utils import (
    send_email_verification, verify_email_token,
    send_password_reset_email, verify_password_reset_token,
    mark_password_reset_token_used
)


# ============ API Views ============

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    User Registration Endpoint
    POST /api/auth/register/
    {
        "email": "user@example.com",
        "name": "John Doe",
        "phone_number": "+1234567890",
        "user_type": "customer",
        "password": "securepass123",
        "password_confirm": "securepass123"
    }
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Send verification email
        base_url = request.data.get('frontend_url', 'http://localhost:3000')
        email_sent = send_email_verification(user, base_url)
        
        if not email_sent:
            return Response({
                'success': True,
                'message': 'User registered successfully, but verification email could not be sent. Please try resending.',
                'user': UserSerializer(user).data,
                'email_sent': False
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': True,
            'message': 'User registered successfully. Please check your email to verify your account.',
            'user': UserSerializer(user).data,
            'email_sent': True
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User Login Endpoint
    POST /api/auth/login/
    {
        "email": "user@example.com",
        "password": "securepass123"
    }
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserDetailSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_view(request):
    """
    Email Verification Endpoint
    POST /api/auth/verify-email/
    {
        "token": "token_string",
        "uid": 1
    }
    """
    serializer = VerifyEmailSerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        uid = serializer.validated_data['uid']
        
        success, message, user = verify_email_token(token, uid)
        
        if success:
            return Response({
                'success': True,
                'message': message,
                'user': UserDetailSerializer(user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email_view(request):
    """
    Resend Verification Email
    POST /api/auth/resend-verification-email/
    {
        "email": "user@example.com",
        "frontend_url": "http://localhost:3000"
    }
    """
    email = request.data.get('email')
    base_url = request.data.get('frontend_url', 'http://localhost:3000')
    
    if not email:
        return Response({
            'success': False,
            'message': 'Email is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        if user.is_email_verified:
            return Response({
                'success': False,
                'message': 'Email is already verified.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email_sent = send_email_verification(user, base_url)
        
        if email_sent:
            return Response({
                'success': True,
                'message': 'Verification email sent successfully.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Failed to send verification email. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No user found with this email address.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """
    Forgot Password - Request Password Reset Email
    POST /api/auth/forgot-password/
    {
        "email": "user@example.com",
        "frontend_url": "http://localhost:3000"
    }
    """
    serializer = ForgotPasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        base_url = request.data.get('frontend_url', 'http://localhost:3000')
        
        user = User.objects.get(email=email)
        email_sent = send_password_reset_email(user, base_url)
        
        if email_sent:
            return Response({
                'success': True,
                'message': 'Password reset email sent successfully. Please check your email.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Failed to send password reset email. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    """
    Reset Password - Verify Token and Set New Password
    POST /api/auth/reset-password/
    {
        "token": "token_string",
        "uid": 1,
        "new_password": "newpass123",
        "confirm_password": "newpass123"
    }
    """
    serializer = PasswordResetSerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        uid = serializer.validated_data['uid']
        new_password = serializer.validated_data['new_password']
        
        success, message, user = verify_password_reset_token(token, uid)
        
        if success:
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            mark_password_reset_token_used(token, uid)
            
            return Response({
                'success': True,
                'message': 'Password reset successfully. You can now login with your new password.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============ Authenticated User Views ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_view(request):
    """
    Get Current User Profile
    GET /api/auth/profile/
    """
    user = request.user
    serializer = UserDetailSerializer(user)
    return Response({
        'success': True,
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update User Profile
    PUT/PATCH /api/auth/update-profile/
    {
        "name": "John Doe",
        "phone_number": "+1234567890",
        "profile_picture": <image_file>
    }
    """
    user = request.user
    serializer = UpdateProfileSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Profile updated successfully.',
            'user': UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Change Password (Authenticated User)
    POST /api/auth/change-password/
    {
        "old_password": "oldpass123",
        "new_password": "newpass123",
        "confirm_password": "newpass123"
    }
    """
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = request.user
        new_password = serializer.validated_data['new_password']
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully.'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout User (Token Blacklist)
    POST /api/auth/logout/
    """
    try:
        refresh_token = request.data.get('refresh_token')
        # Token blacklisting would require setting up token blacklist app
        # For now, just return success as JWT logout is typically client-side
        return Response({
            'success': True,
            'message': 'Logout successful.'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
