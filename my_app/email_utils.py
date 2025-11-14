"""
Email utilities for sending verification and password reset emails
"""
import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import EmailVerificationToken, PasswordResetToken


def generate_secure_token():
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for i in range(32))
    return token


def send_email_verification(user, base_url):
    """
    Send email verification link to user
    
    Args:
        user: User instance
        base_url: Base URL of your frontend (e.g., 'https://yourfrontend.com')
    """
    try:
        # Generate token
        token = generate_secure_token()
        
        # Delete existing token if any
        EmailVerificationToken.objects.filter(user=user).delete()
        
        # Create token entry
        expires_at = timezone.now() + timedelta(seconds=settings.EMAIL_VERIFICATION_TOKEN_EXPIRY)
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # Create verification link
        verification_link = f"{base_url}/verify-email?token={token}&uid={user.id}"
        
        # Email content
        subject = "Email Verification - CalmSpace"
        message = f"""
        Hello {user.name},
        
        Thank you for signing up with CalmSpace. Please verify your email address by clicking the link below:
        
        {verification_link}
        
        This link will expire in 24 hours.
        
        If you did not sign up for CalmSpace, please ignore this email.
        
        Best regards,
        CalmSpace Team
        """
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Email Verification - CalmSpace</h2>
                <p>Hello {user.name},</p>
                <p>Thank you for signing up with CalmSpace. Please verify your email address by clicking the button below:</p>
                <p>
                    <a href="{verification_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Verify Email
                    </a>
                </p>
                <p>Or copy and paste this link in your browser:</p>
                <p>{verification_link}</p>
                <p style="color: #666;">This link will expire in 24 hours.</p>
                <p style="color: #999;">If you did not sign up for CalmSpace, please ignore this email.</p>
                <p>Best regards,<br>CalmSpace Team</p>
            </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return False


def verify_email_token(token, user_id):
    """
    Verify email token
    
    Args:
        token: Token string
        user_id: User ID
        
    Returns:
        Tuple: (success: bool, message: str, user: User or None)
    """
    try:
        email_token = EmailVerificationToken.objects.get(token=token, user_id=user_id)
        
        if not email_token.is_valid():
            return False, "Token has expired or already been used.", None
        
        # Mark token as used
        email_token.is_used = True
        email_token.save()
        
        # Mark user email as verified
        user = email_token.user
        user.is_email_verified = True
        user.save()
        
        return True, "Email verified successfully!", user
    except EmailVerificationToken.DoesNotExist:
        return False, "Invalid token.", None


def send_password_reset_email(user, base_url):
    """
    Send password reset link to user
    
    Args:
        user: User instance
        base_url: Base URL of your frontend (e.g., 'https://yourfrontend.com')
    """
    try:
        # Generate token
        token = generate_secure_token()
        
        # Create token entry
        expires_at = timezone.now() + timedelta(seconds=settings.PASSWORD_RESET_TOKEN_EXPIRY)
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # Create reset link
        reset_link = f"{base_url}/reset-password?token={token}&uid={user.id}"
        
        # Email content
        subject = "Password Reset Request - CalmSpace"
        message = f"""
        Hello {user.name},
        
        You requested a password reset. Click the link below to reset your password:
        
        {reset_link}
        
        This link will expire in 24 hours.
        
        If you did not request a password reset, please ignore this email.
        
        Best regards,
        CalmSpace Team
        """
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Password Reset Request - CalmSpace</h2>
                <p>Hello {user.name},</p>
                <p>You requested a password reset. Click the button below to reset your password:</p>
                <p>
                    <a href="{reset_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Reset Password
                    </a>
                </p>
                <p>Or copy and paste this link in your browser:</p>
                <p>{reset_link}</p>
                <p style="color: #666;">This link will expire in 24 hours.</p>
                <p style="color: #999;">If you did not request a password reset, please ignore this email.</p>
                <p>Best regards,<br>CalmSpace Team</p>
            </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False


def verify_password_reset_token(token, user_id):
    """
    Verify password reset token
    
    Args:
        token: Token string
        user_id: User ID
        
    Returns:
        Tuple: (success: bool, message: str, user: User or None)
    """
    try:
        reset_token = PasswordResetToken.objects.get(token=token, user_id=user_id)
        
        if not reset_token.is_valid():
            return False, "Token has expired or already been used.", None
        
        user = reset_token.user
        return True, "Token is valid.", user
    except PasswordResetToken.DoesNotExist:
        return False, "Invalid token.", None


def mark_password_reset_token_used(token, user_id):
    """Mark password reset token as used after successful reset"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token, user_id=user_id)
        reset_token.is_used = True
        reset_token.save()
        return True
    except PasswordResetToken.DoesNotExist:
        return False
