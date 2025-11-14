# 🧪 Testing & Verification Guide

## Pre-Testing Checklist

Before testing the authentication system, ensure:

- [ ] All files have been created/modified as per implementation
- [ ] `.env` file is configured with email settings
- [ ] Migrations have been run: `python manage.py migrate`
- [ ] User groups have been created: `python manage.py setup_user_groups`
- [ ] Django development server is running: `python manage.py runserver`

---

## Quick Verification Commands

### 1. Check Migrations

```bash
python manage.py showmigrations my_app
```

Expected output should show EmailVerificationToken and PasswordResetToken migrations as applied.

### 2. Verify User Model

```bash
python manage.py shell
>>> from my_app.models import User, EmailVerificationToken, PasswordResetToken
>>> print(User._meta.get_fields())
```

Should show all custom fields: phone_number, profile_picture, user_type, is_email_verified, etc.

### 3. Check Groups Created

```bash
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> groups = Group.objects.all()
>>> for group in groups:
...     print(f"{group.name}: {group.permissions.count()} permissions")
```

Expected output:

```
Admin: <all permissions>
Staff: <limited permissions>
Customer: <basic permissions>
Therapist: <therapist permissions>
```

### 4. Test Email Configuration

```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail(
...     'Test Email',
...     'This is a test email.',
...     'your-email@gmail.com',
...     ['recipient@example.com'],
... )
```

Should return 1 (success) or raise an error with helpful message.

---

## API Testing with curl

### Test 1: Register User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "name": "Test User",
    "phone_number": "+1234567890",
    "user_type": "customer",
    "password": "SecurePass@123",
    "password_confirm": "SecurePass@123",
    "frontend_url": "http://localhost:3000"
  }'
```

**Expected Response:**

- Status: 201 Created
- `success`: true
- `email_sent`: true (if email configured) or false (if email failed)
- User object with `is_email_verified: false`

**Check for:**

- Email should be received (check spam folder if not in inbox)
- Email should contain verification link with token and uid

### Test 2: Try Login Before Email Verification

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass@123"
  }'
```

**Expected Response:**

- Status: 400 Bad Request
- `success`: false
- `message`: "Please verify your email before logging in."

### Test 3: Verify Email

```bash
# Replace TOKEN and UID with values from email link
curl -X POST http://localhost:8000/api/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_FROM_EMAIL",
    "uid": 1
  }'
```

**Expected Response:**

- Status: 200 OK
- `success`: true
- `message`: "Email verified successfully!"
- User object with `is_email_verified: true`

### Test 4: Login After Email Verification

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass@123"
  }'
```

**Expected Response:**

- Status: 200 OK
- `success`: true
- `tokens` object with `access` and `refresh` tokens
- User details

**Save the access_token for subsequent requests**

### Test 5: Get Profile

```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**

- Status: 200 OK
- Current user's profile data

### Test 6: Update Profile

```bash
curl -X PUT http://localhost:8000/api/auth/update-profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "name=Updated Name" \
  -F "phone_number=+9876543210"
```

**Expected Response:**

- Status: 200 OK
- Updated user data

### Test 7: Change Password (Authenticated)

```bash
curl -X POST http://localhost:8000/api/auth/change-password/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass@123",
    "new_password": "NewSecure@123",
    "confirm_password": "NewSecure@123"
  }'
```

**Expected Response:**

- Status: 200 OK
- `success`: true
- `message`: "Password changed successfully."

### Test 8: Request Password Reset

```bash
curl -X POST http://localhost:8000/api/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "frontend_url": "http://localhost:3000"
  }'
```

**Expected Response:**

- Status: 200 OK
- `success`: true
- Email should contain password reset link

### Test 9: Reset Password

```bash
# Replace TOKEN and UID with values from reset email
curl -X POST http://localhost:8000/api/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TOKEN_FROM_EMAIL",
    "uid": 1,
    "new_password": "ResetPass@123",
    "confirm_password": "ResetPass@123"
  }'
```

**Expected Response:**

- Status: 200 OK
- `success`: true
- `message`: "Password reset successfully..."

### Test 10: Login with New Password

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "ResetPass@123"
  }'
```

**Expected Response:**

- Status: 200 OK
- Successfully logged in with new password

---

## Testing with Postman

1. Import `CalmSpace_API.postman_collection.json` into Postman
2. Update environment variables:
   - `{{access_token}}` - Will be set after login
   - `{{refresh_token}}` - Will be set after login
3. Run requests in this order:
   - Register User
   - Try Login (should fail)
   - Verify Email (use token from email)
   - Login User (should succeed)
   - Get Profile
   - Update Profile
   - Change Password
   - Request Password Reset
   - Reset Password
   - Login again with new password

---

## Role-Based Access Control Testing

### Test Admin-Only Endpoint

First, create an admin user:

```bash
python manage.py shell
>>> from my_app.models import User
>>> admin = User.objects.create_user(
...     email='admin@test.com',
...     name='Admin User',
...     password='AdminPass@123',
...     user_type='admin',
...     is_staff=True,
...     is_superuser=True,
...     is_email_verified=True
... )
```

Then test with admin token:

```bash
# Login as admin
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "AdminPass@123"
  }'

# Save admin access token, then use it in protected endpoint
curl -X GET http://localhost:8000/api/some-admin-endpoint/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Test Staff-Only Endpoint

Create staff user:

```bash
python manage.py shell
>>> from my_app.models import User
>>> staff = User.objects.create_user(
...     email='staff@test.com',
...     name='Staff User',
...     password='StaffPass@123',
...     user_type='staff',
...     is_staff=True,
...     is_email_verified=True
... )
```

### Test Customer User

Should succeed for basic endpoints, fail for admin endpoints:

```bash
# Login as customer (already created in Test 1)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "ResetPass@123"
  }'

# Use customer token to access endpoints
# Should work for: GET /api/users/, GET /api/profiles/
# Should fail for: DELETE /api/users/, POST /api/users/ (if restricted)
```

---

## Database Verification

### Check Users Table

```bash
python manage.py shell
>>> from my_app.models import User
>>> users = User.objects.all()
>>> for user in users:
...     print(f"Email: {user.email}, Type: {user.user_type}, Verified: {user.is_email_verified}")
```

### Check Verification Tokens

```bash
python manage.py shell
>>> from my_app.models import EmailVerificationToken
>>> tokens = EmailVerificationToken.objects.all()
>>> for token in tokens:
...     print(f"User: {token.user.email}, Valid: {token.is_valid()}, Used: {token.is_used}")
```

### Check Password Reset Tokens

```bash
python manage.py shell
>>> from my_app.models import PasswordResetToken
>>> tokens = PasswordResetToken.objects.all()
>>> for token in tokens:
...     print(f"User: {token.user.email}, Valid: {token.is_valid()}, Used: {token.is_used}")
```

---

## Error Handling Tests

### Test 1: Invalid Email Format

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "not-an-email",
    "name": "Test",
    "password": "Pass@123",
    "password_confirm": "Pass@123"
  }'
```

**Expected:** 400 Bad Request with email validation error

### Test 2: Passwords Don't Match

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test",
    "password": "Pass@123",
    "password_confirm": "DifferentPass@123"
  }'
```

**Expected:** 400 Bad Request with password mismatch error

### Test 3: Duplicate Email

```bash
# Register once, then try again with same email
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "duplicate@example.com",
    "name": "Test 1",
    "password": "Pass@123",
    "password_confirm": "Pass@123"
  }'

# Try registering again
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "duplicate@example.com",
    "name": "Test 2",
    "password": "Pass@123",
    "password_confirm": "Pass@123"
  }'
```

**Expected:** 400 Bad Request with "email already exists" error

### Test 4: Invalid Token for Email Verification

```bash
curl -X POST http://localhost:8000/api/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "invalid-token",
    "uid": 1
  }'
```

**Expected:** 400 Bad Request with "Invalid token" message

### Test 5: Expired Token

```bash
# Wait 24+ hours (or modify token expiry in code to test)
# Try to verify with old token
curl -X POST http://localhost:8000/api/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "old-token",
    "uid": 1
  }'
```

**Expected:** 400 Bad Request with "Token has expired" message

### Test 6: Access Protected Route Without Token

```bash
curl -X GET http://localhost:8000/api/auth/profile/
```

**Expected:** 401 Unauthorized with "Authentication credentials were not provided"

### Test 7: Invalid JWT Token

```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer invalid-token"
```

**Expected:** 401 Unauthorized with "Invalid token" message

---

## Performance Testing

### Test 1: Multiple Registration Requests

```bash
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/auth/register/ \
    -H "Content-Type: application/json" \
    -d "{
      \"email\": \"user$i@example.com\",
      \"name\": \"User $i\",
      \"password\": \"Pass@123\",
      \"password_confirm\": \"Pass@123\"
    }"
  echo "\nUser $i registered"
done
```

**Check:** Server should handle all requests without errors

### Test 2: Concurrent Login Requests

Use Apache Bench or similar tool:

```bash
ab -n 100 -c 10 -p login.json -T "application/json" \
  http://localhost:8000/api/auth/login/
```

---

## Security Testing

### Test 1: SQL Injection

Try to inject SQL in email field:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com\" OR \"1\"=\"1",
    "password": "pass"
  }'
```

**Expected:** Invalid email error or failed login (never bypassed)

### Test 2: Password in Response

Verify passwords are never returned:

```bash
# Check register response
# Check login response
# Check profile response
# Password should NEVER appear in any response
```

**Expected:** No password field in any response

### Test 3: Token Reuse

Try using same token twice:

```bash
# First verification
curl -X POST http://localhost:8000/api/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{"token": "TOKEN", "uid": 1}'

# Second verification with same token
curl -X POST http://localhost:8000/api/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{"token": "TOKEN", "uid": 1}'
```

**Expected:** First succeeds, second fails with "token already used"

---

## Final Verification Checklist

- [ ] All 10+ API endpoints working
- [ ] Email verification flow complete
- [ ] Password reset flow complete
- [ ] Role-based access working
- [ ] Profile management working
- [ ] Error handling working
- [ ] Tokens expiring correctly
- [ ] Security measures in place
- [ ] Database tables created
- [ ] User groups created
- [ ] Serializers validating correctly
- [ ] Permissions enforcing correctly

---

## What To Do If Tests Fail

1. **Check Django Logs** - Look for error messages in console
2. **Check Database** - Verify tables exist with correct schema
3. **Check Email Config** - Test email sending separately
4. **Check .env File** - Verify all required variables are set
5. **Check Migrations** - Run `python manage.py migrate --fake-initial` if needed
6. **Check Permissions** - Verify user has correct user_type
7. **Check Tokens** - Verify tokens haven't expired
8. **Check Frontend URL** - Ensure frontend_url is correct in requests

---

## Success Indicators

✅ All tests pass
✅ Emails being sent successfully
✅ Tokens valid and expiring correctly
✅ Permissions working as expected
✅ Profile images uploading
✅ Passwords hashing correctly
✅ JWT tokens valid
✅ Error messages helpful
✅ Database clean and organized
✅ Code following Django best practices

---

**Status:** Ready for Production Deployment (after additional security testing)
