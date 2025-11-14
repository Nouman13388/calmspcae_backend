# CalmSpace Backend - Authentication & Role-Based Access Control

This document provides a comprehensive guide to the authentication system, email verification, password reset, and role-based access control implemented in the CalmSpace backend.

## Table of Contents

1. [Setup Instructions](#setup-instructions)
2. [Custom User Model](#custom-user-model)
3. [Authentication Endpoints](#authentication-endpoints)
4. [Email Verification](#email-verification)
5. [Password Reset](#password-reset)
6. [Role-Based Access Control](#role-based-access-control)
7. [Profile Management](#profile-management)
8. [Permissions & Decorators](#permissions--decorators)

---

## Setup Instructions

### 1. Environment Variables

Add the following to your `.env` file:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Token Expiry (in seconds)
EMAIL_VERIFICATION_TOKEN_EXPIRY=86400  # 24 hours
PASSWORD_RESET_TOKEN_EXPIRY=86400      # 24 hours
```

**Note for Gmail:** Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

The following packages are already included:

- `djangorestframework`
- `djangorestframework-simplejwt`
- `django-environ`
- `pillow` (for image uploads)

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Setup User Groups and Permissions

```bash
python manage.py setup_user_groups
```

This creates four groups:

- **Admin** - Full access to all resources
- **Staff** - Limited access for internal team
- **Customer** - Basic access for end users
- **Therapist** - Access for mental health professionals

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

---

## Custom User Model

The custom `User` model extends Django's `AbstractBaseUser` with additional fields:

### Fields

| Field               | Type          | Description                                       |
| ------------------- | ------------- | ------------------------------------------------- |
| `email`             | EmailField    | Unique email (used as username)                   |
| `name`              | CharField     | User's full name                                  |
| `phone_number`      | CharField     | Optional phone number                             |
| `profile_picture`   | ImageField    | Optional profile image                            |
| `user_type`         | CharField     | One of: `customer`, `staff`, `admin`, `therapist` |
| `is_email_verified` | BooleanField  | Email verification status                         |
| `is_active`         | BooleanField  | Account active status                             |
| `is_staff`          | BooleanField  | Django staff status                               |
| `is_superuser`      | BooleanField  | Django superuser status                           |
| `created_at`        | DateTimeField | Account creation time                             |
| `updated_at`        | DateTimeField | Last update time                                  |
| `last_login`        | DateTimeField | Last login time                                   |

### Usage

```python
from my_app.models import User

# Create a regular user
user = User.objects.create_user(
    email='customer@example.com',
    name='John Doe',
    phone_number='+1234567890',
    user_type='customer',
    password='securepass123'
)

# Create a superuser
User.objects.create_superuser(
    email='admin@example.com',
    name='Admin User',
    password='securepass123'
)
```

---

## Authentication Endpoints

All authentication endpoints are prefixed with `/api/auth/`

### 1. Register User

**Endpoint:** `POST /api/auth/register/`

**Request:**

```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "phone_number": "+1234567890",
  "user_type": "customer",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "frontend_url": "http://localhost:3000"
}
```

**Response:**

```json
{
  "success": true,
  "message": "User registered successfully. Please check your email to verify your account.",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "phone_number": "+1234567890",
    "user_type": "customer",
    "is_email_verified": false,
    "created_at": "2024-11-14T10:30:00Z"
  },
  "email_sent": true
}
```

### 2. Login User

**Endpoint:** `POST /api/auth/login/`

**Request:**

```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "is_email_verified": true,
    "user_type": "customer"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 3. Logout User

**Endpoint:** `POST /api/auth/logout/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**

```json
{
  "success": true,
  "message": "Logout successful."
}
```

---

## Email Verification

### 1. Verify Email

**Endpoint:** `POST /api/auth/verify-email/`

**Request:**

```json
{
  "token": "token_string",
  "uid": 1
}
```

**Response:**

```json
{
  "success": true,
  "message": "Email verified successfully!",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_email_verified": true
  }
}
```

### 2. Resend Verification Email

**Endpoint:** `POST /api/auth/resend-verification-email/`

**Request:**

```json
{
  "email": "user@example.com",
  "frontend_url": "http://localhost:3000"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Verification email sent successfully."
}
```

### Frontend Integration

The verification link sent to the user's email will look like:

```
http://localhost:3000/verify-email?token=<token>&uid=<user_id>
```

Your frontend should:

1. Extract `token` and `uid` from URL parameters
2. Call the verify endpoint with these values
3. Show success/error message to user

---

## Password Reset

### 1. Request Password Reset

**Endpoint:** `POST /api/auth/forgot-password/`

**Request:**

```json
{
  "email": "user@example.com",
  "frontend_url": "http://localhost:3000"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Password reset email sent successfully. Please check your email."
}
```

### 2. Reset Password

**Endpoint:** `POST /api/auth/reset-password/`

**Request:**

```json
{
  "token": "token_string",
  "uid": 1,
  "new_password": "newpass123",
  "confirm_password": "newpass123"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Password reset successfully. You can now login with your new password."
}
```

### Frontend Integration

The password reset link sent to the user's email will look like:

```
http://localhost:3000/reset-password?token=<token>&uid=<user_id>
```

Your frontend should:

1. Extract `token` and `uid` from URL parameters
2. Show form to enter new password
3. Call the reset endpoint with these values
4. Redirect to login on success

---

## Role-Based Access Control

### User Types

- **Customer** - Regular end users with basic access
- **Staff** - Internal team members with limited administrative access
- **Admin** - Full administrative access
- **Therapist** - Mental health professionals with specific permissions

### Permission Classes

Use these in your ViewSets and APIViews:

```python
from my_app.permissions import IsAdmin, IsStaff, IsTherapist, IsCustomer, IsEmailVerified

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]  # Only admins can access
```

Available permission classes:

- `IsAdmin` - User is admin
- `IsStaff` - User is staff
- `IsAdminOrStaff` - User is admin or staff
- `IsCustomer` - User is customer
- `IsTherapist` - User is therapist
- `IsEmailVerified` - User's email is verified
- `IsOwner` - User owns the object (check object permission)

### Using Decorators

```python
from rest_framework.decorators import api_view, permission_classes
from my_app.permissions import admin_required, staff_required, therapist_required

@api_view(['GET'])
@admin_required  # Only admin users can access
def admin_only_view(request):
    return Response({'message': 'Admin only'})

@api_view(['GET'])
@staff_required  # Only staff can access
def staff_only_view(request):
    return Response({'message': 'Staff only'})

@api_view(['GET'])
@therapist_required  # Only therapists can access
def therapist_only_view(request):
    return Response({'message': 'Therapist only'})
```

### Using RoleBasedAccessMixin

```python
from my_app.permissions import RoleBasedAccessMixin
from rest_framework import viewsets

class UserViewSet(RoleBasedAccessMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Define permissions per action
    role_based_permissions = {
        'list': ['admin', 'staff'],      # Only admin and staff can list users
        'create': ['admin'],               # Only admin can create
        'update': ['admin', 'staff'],      # Admin and staff can update
        'destroy': ['admin'],              # Only admin can delete
        'retrieve': ['admin', 'staff', 'customer'],  # Anyone can view individual user
    }
```

---

## Profile Management

### 1. Get Current User Profile

**Endpoint:** `GET /api/auth/profile/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**

```json
{
  "success": true,
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "phone_number": "+1234567890",
    "profile_picture": "https://...",
    "user_type": "customer",
    "is_email_verified": true,
    "is_active": true,
    "created_at": "2024-11-14T10:30:00Z",
    "updated_at": "2024-11-14T10:35:00Z"
  }
}
```

### 2. Update Profile

**Endpoint:** `PUT/PATCH /api/auth/update-profile/`

**Headers:** `Authorization: Bearer <access_token>`

**Request (multipart/form-data):**

```
name: John Doe Updated
phone_number: +9876543210
profile_picture: <image_file>
```

**Response:**

```json
{
  "success": true,
  "message": "Profile updated successfully.",
  "user": {
    "id": 1,
    "name": "John Doe Updated",
    "email": "user@example.com",
    "phone_number": "+9876543210",
    "profile_picture": "https://...",
    "user_type": "customer"
  }
}
```

### 3. Change Password

**Endpoint:** `POST /api/auth/change-password/`

**Headers:** `Authorization: Bearer <access_token>`

**Request:**

```json
{
  "old_password": "securepass123",
  "new_password": "newsecurepass123",
  "confirm_password": "newsecurepass123"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Password changed successfully."
}
```

---

## Permissions & Decorators

### Permission Classes for ViewSets

```python
from rest_framework import viewsets
from my_app.permissions import IsAdmin, IsEmailVerified

class RestrictedViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer

    # Require both admin and email verification
    permission_classes = [IsAdmin, IsEmailVerified]
```

### Custom Permission Check in Views

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_view(request):
    user = request.user

    # Check user type
    if user.user_type == 'admin':
        # Admin-specific logic
        pass
    elif user.user_type == 'staff':
        # Staff-specific logic
        pass
    elif user.user_type == 'customer':
        # Customer-specific logic
        pass

    # Check email verification
    if not user.is_email_verified:
        return Response({'error': 'Email not verified'}, status=403)

    return Response({'data': 'Your data'})
```

### Assigning Users to Groups

```python
from django.contrib.auth.models import Group

# Get user
user = User.objects.get(email='user@example.com')

# Get group
admin_group = Group.objects.get(name='Admin')

# Add user to group
user.groups.add(admin_group)

# Remove from group
user.groups.remove(admin_group)

# Get all groups for user
user_groups = user.groups.all()

# Check if user is in group
if admin_group in user.groups.all():
    print("User is admin")
```

---

## Token Generation & Verification

### Email Verification Token

```python
from my_app.email_utils import send_email_verification, verify_email_token

# Send verification email
user = User.objects.get(email='user@example.com')
send_email_verification(user, 'http://localhost:3000')

# Verify token
success, message, user = verify_email_token('token_string', user_id)
```

### Password Reset Token

```python
from my_app.email_utils import (
    send_password_reset_email,
    verify_password_reset_token,
    mark_password_reset_token_used
)

# Send password reset email
user = User.objects.get(email='user@example.com')
send_password_reset_email(user, 'http://localhost:3000')

# Verify token
success, message, user = verify_password_reset_token('token_string', user_id)

# Mark as used after password change
mark_password_reset_token_used('token_string', user_id)
```

---

## Frontend Integration Examples

### React Example

```javascript
// Register
const register = async (formData) => {
  const response = await fetch("http://localhost:8000/api/auth/register/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...formData,
      frontend_url: window.location.origin,
    }),
  });
  const data = await response.json();
  return data;
};

// Login
const login = async (email, password) => {
  const response = await fetch("http://localhost:8000/api/auth/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  localStorage.setItem("access_token", data.tokens.access);
  localStorage.setItem("refresh_token", data.tokens.refresh);
  return data;
};

// Verify Email
const verifyEmail = async (token, uid) => {
  const response = await fetch("http://localhost:8000/api/auth/verify-email/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, uid }),
  });
  return response.json();
};

// Get Profile
const getProfile = async () => {
  const token = localStorage.getItem("access_token");
  const response = await fetch("http://localhost:8000/api/auth/profile/", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.json();
};

// Update Profile
const updateProfile = async (formData) => {
  const token = localStorage.getItem("access_token");
  const response = await fetch(
    "http://localhost:8000/api/auth/update-profile/",
    {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}` },
      body: formData, // Use FormData for file upload
    }
  );
  return response.json();
};
```

---

## Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "message": "Error description",
  "field_errors": {
    "email": ["User with this email already exists."],
    "password": ["Password is too short."]
  }
}
```

Common HTTP Status Codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Testing

### Create Test Users

```bash
python manage.py shell

from my_app.models import User
from django.contrib.auth.models import Group

# Create admin
admin = User.objects.create_user(
    email='admin@test.com',
    name='Admin User',
    user_type='admin',
    password='testpass123',
    is_staff=True,
    is_superuser=True,
    is_email_verified=True
)

# Create staff
staff = User.objects.create_user(
    email='staff@test.com',
    name='Staff User',
    user_type='staff',
    password='testpass123',
    is_staff=True,
    is_email_verified=True
)

# Create customer
customer = User.objects.create_user(
    email='customer@test.com',
    name='Customer User',
    user_type='customer',
    password='testpass123',
    is_email_verified=True
)
```

---

## Troubleshooting

### Email not sending?

- Check `.env` file has correct email credentials
- For Gmail, use [App Password](https://support.google.com/accounts/answer/185833)
- Check Django logs for SMTP errors
- Verify `DEFAULT_FROM_EMAIL` is set correctly

### Token expired?

- Tokens expire after 24 hours by default
- User can request a new verification/reset email
- Adjust `EMAIL_VERIFICATION_TOKEN_EXPIRY` and `PASSWORD_RESET_TOKEN_EXPIRY` in settings

### Login failing after email verification?

- Ensure user's `is_email_verified` is set to `True`
- Check user is in appropriate group/role
- Verify JWT configuration in settings

### Image upload not working?

- Ensure `MEDIA_URL` and `MEDIA_ROOT` are configured
- Check file permissions on media directory
- Verify Pillow is installed: `pip install pillow`

---

## Best Practices

1. **Always use HTTPS in production** - JWT tokens should be transmitted securely
2. **Store tokens securely** - Use httpOnly cookies or secure storage
3. **Implement token refresh** - Don't rely on long-lived access tokens
4. **Validate email before key operations** - Require email verification
5. **Log security events** - Track failed logins, permission denials
6. **Use strong passwords** - Enforce password complexity
7. **Rate limit endpoints** - Prevent brute force attacks on auth endpoints
8. **Regular backups** - Backup database before running migrations

---

## Support

For issues or questions, refer to:

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Token Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
