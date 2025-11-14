# CalmSpace Backend Implementation Summary

## 🎉 What's Been Implemented

### ✅ Custom User Model

- Extended Django's `AbstractBaseUser` with custom fields
- Added fields: `phone_number`, `user_type`, `profile_picture`, `is_email_verified`, and more
- User types: `customer`, `staff`, `admin`, `therapist`
- Located in: `my_app/models.py`

### ✅ Email Verification System

- Token-based secure email verification
- Tokens stored in database with expiration (24 hours by default)
- EmailVerificationToken model for tracking verification
- Automatic token generation and validation
- Located in: `my_app/models.py`, `my_app/email_utils.py`

### ✅ Password Reset (Forgot Password)

- Secure token-based password reset flow
- PasswordResetToken model with expiration tracking
- One-time use tokens (marked as used after password reset)
- Located in: `my_app/models.py`, `my_app/email_utils.py`

### ✅ Role-Based Access Control (RBAC)

- Four user groups: Admin, Staff, Customer, Therapist
- Permission classes for ViewSets: `IsAdmin`, `IsStaff`, `IsTherapist`, `IsCustomer`
- Decorators for view-level control: `@admin_required`, `@staff_required`, etc.
- RoleBasedAccessMixin for granular permission per action
- Located in: `my_app/permissions.py`

### ✅ Profile Management

- Upload profile images
- Update user information (name, email, phone, profile picture)
- Change password (authenticated users only)
- Located in: `my_app/auth_views.py`

---

## 📁 Files Created/Modified

### New Files Created:

1. **`my_app/auth_serializers.py`**

   - Authentication serializers (Register, Login, VerifyEmail, etc.)
   - Profile update serializers

2. **`my_app/auth_views.py`**

   - All authentication endpoints
   - Email verification, password reset
   - Profile management views

3. **`my_app/email_utils.py`**

   - Email sending functions
   - Token generation and validation
   - Security utilities

4. **`my_app/management/commands/setup_user_groups.py`**

   - Management command to create user groups and assign permissions

5. **`AUTHENTICATION_GUIDE.md`**

   - Comprehensive documentation (200+ lines)
   - API endpoints with examples
   - Frontend integration guide
   - Troubleshooting section

6. **`CalmSpace_API.postman_collection.json`**

   - Postman collection for testing all endpoints

7. **`.env.example`**
   - Example environment configuration

### Modified Files:

1. **`my_app/models.py`**

   - Enhanced User model with custom fields
   - Added EmailVerificationToken model
   - Added PasswordResetToken model

2. **`my_app/permissions.py`**

   - Added new role-based permission classes
   - Added decorator functions for view-level control

3. **`my_app/urls.py`**

   - Added authentication endpoints

4. **`calmspcae_backend/settings.py`**
   - Added AUTH_USER_MODEL configuration
   - Added email configuration settings
   - Added JWT configuration

---

## 🚀 Quick Start Guide

### Step 1: Setup Environment Variables

Create a `.env` file in project root (copy from `.env.example`):

```env
# Email Configuration (Gmail Example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**For Gmail:**

1. Enable 2-Step Verification
2. Generate [App Password](https://support.google.com/accounts/answer/185833)
3. Use the app password above

### Step 2: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Setup User Groups

```bash
python manage.py setup_user_groups
```

### Step 4: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 5: Test the API

Use Postman collection: `CalmSpace_API.postman_collection.json`

Or use curl:

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"John","password":"pass123","password_confirm":"pass123","user_type":"customer"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'
```

---

## 📚 API Endpoints

### Authentication

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### Email Verification

- `POST /api/auth/verify-email/` - Verify email with token
- `POST /api/auth/resend-verification-email/` - Resend verification email

### Password Reset

- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Reset password with token

### Profile

- `GET /api/auth/profile/` - Get current user profile
- `PUT/PATCH /api/auth/update-profile/` - Update profile
- `POST /api/auth/change-password/` - Change password

---

## 🔐 Key Security Features

1. **Secure Token Generation** - Using `secrets` module for cryptographic randomness
2. **Token Expiration** - Tokens expire after 24 hours by default
3. **One-Time Tokens** - Reset and verification tokens are marked as used
4. **Password Hashing** - Django's built-in password hashing (PBKDF2)
5. **JWT Tokens** - For API authentication
6. **Email Verification** - Users must verify email before login
7. **Rate Limiting Ready** - Easy to add with django-ratelimit

---

## 💡 Usage Examples

### Restrict View to Admins Only

```python
from rest_framework.decorators import api_view
from my_app.permissions import admin_required

@api_view(['GET'])
@admin_required
def admin_dashboard(request):
    return Response({'data': 'admin only'})
```

### Role-Based ViewSet

```python
from my_app.permissions import RoleBasedAccessMixin

class UserViewSet(RoleBasedAccessMixin, viewsets.ModelViewSet):
    role_based_permissions = {
        'list': ['admin', 'staff'],
        'destroy': ['admin'],
    }
```

### Check User Type in View

```python
if request.user.user_type == 'admin':
    # Admin logic
elif request.user.user_type == 'therapist':
    # Therapist logic
```

---

## 🧪 Testing Checklist

- [ ] Register a new user
- [ ] Check email verification link
- [ ] Verify email
- [ ] Try logging in before verification (should fail)
- [ ] Try logging in after verification (should work)
- [ ] Request password reset
- [ ] Check password reset email
- [ ] Reset password with token
- [ ] Login with new password
- [ ] Update profile with image
- [ ] Change password while logged in
- [ ] Test admin-only endpoint (should be forbidden for non-admins)
- [ ] Test staff-only endpoint

---

## 📖 Documentation

Comprehensive documentation is available in `AUTHENTICATION_GUIDE.md` including:

- Full API endpoint reference
- Frontend integration examples
- Error handling
- Best practices
- Troubleshooting guide

---

## 🔧 Customization Options

### Change Token Expiry Time

In `settings.py`:

```python
EMAIL_VERIFICATION_TOKEN_EXPIRY = 12 * 60 * 60  # 12 hours
PASSWORD_RESET_TOKEN_EXPIRY = 12 * 60 * 60      # 12 hours
```

### Add More User Types

In `User` model:

```python
USER_TYPE_CHOICES = (
    ('customer', 'Customer'),
    ('staff', 'Staff'),
    ('admin', 'Admin'),
    ('therapist', 'Therapist'),
    ('partner', 'Partner'),  # Add new type
)
```

### Customize Email Template

Edit in `my_app/email_utils.py`:

```python
html_message = f"""
<html>
    <!-- Customize your email template -->
</html>
"""
```

---

## 🐛 Common Issues & Solutions

### Issue: Email not sending

**Solution:** Check `.env` file credentials, ensure app password for Gmail

### Issue: Token expired errors

**Solution:** Increase token expiry in settings.py or implement token refresh

### Issue: CORS errors on frontend

**Solution:** Check CORS_ALLOWED_ORIGINS in settings.py

### Issue: Migrations not found

**Solution:** Run `python manage.py makemigrations my_app`

---

## 📝 Next Steps

1. **Add Rate Limiting** - Prevent brute force attacks

   ```bash
   pip install django-ratelimit
   ```

2. **Add Token Blacklist** - For logout functionality

   ```bash
   pip install djangorestframework-simplejwt[blacklist]
   ```

3. **Add Social Authentication** - Google, Facebook login

   ```bash
   pip install django-allauth
   ```

4. **Add Two-Factor Authentication** - For enhanced security

   ```bash
   pip install django-otp
   ```

5. **Add Email Templates** - Use django-templated-email
   ```bash
   pip install django-templated-email
   ```

---

## 📞 Support

For detailed information, refer to:

- `AUTHENTICATION_GUIDE.md` - Complete API documentation
- `my_app/auth_views.py` - View implementation
- `my_app/email_utils.py` - Email utilities
- `my_app/permissions.py` - Permission classes

---

## ✨ Features Summary

| Feature            | Status | Location                      |
| ------------------ | ------ | ----------------------------- |
| Custom User Model  | ✅     | `models.py`                   |
| Email Verification | ✅     | `models.py`, `email_utils.py` |
| Password Reset     | ✅     | `models.py`, `email_utils.py` |
| RBAC               | ✅     | `permissions.py`              |
| Profile Management | ✅     | `auth_views.py`               |
| JWT Authentication | ✅     | `settings.py`                 |
| Group Permissions  | ✅     | `management/commands/`        |
| API Endpoints      | ✅     | `auth_views.py`, `urls.py`    |

---

**Implementation Date:** November 14, 2025

**Status:** 🟢 Ready for Development & Testing
