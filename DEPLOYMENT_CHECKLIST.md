# 📋 Developer Checklist - CalmSpace Authentication Implementation

## Pre-Deployment Checklist

### Phase 1: Setup & Configuration ✓

- [ ] Clone/Pull latest code
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy `.env.example` to `.env`
- [ ] Configure `.env` with database credentials
- [ ] Configure `.env` with email settings (Gmail App Password)
- [ ] Verify all required `.env` variables are set

### Phase 2: Database Setup ✓

- [ ] Run migrations: `python manage.py makemigrations`
- [ ] Apply migrations: `python manage.py migrate`
- [ ] Verify migration files created in `my_app/migrations/`
- [ ] Check database tables created:
  - [ ] `auth_user` (or custom user table)
  - [ ] `email_verification_token_table`
  - [ ] `password_reset_token_table`
  - [ ] `auth_group` (for permissions)

### Phase 3: Data Initialization ✓

- [ ] Run setup command: `python manage.py setup_user_groups`
- [ ] Verify 4 groups created: Admin, Staff, Customer, Therapist
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Verify superuser created in database

### Phase 4: File Verification ✓

**New Files:**

- [ ] `my_app/auth_serializers.py` (600+ lines)
- [ ] `my_app/auth_views.py` (400+ lines)
- [ ] `my_app/email_utils.py` (300+ lines)
- [ ] `my_app/management/commands/setup_user_groups.py`

**Modified Files:**

- [ ] `my_app/models.py` - Enhanced User model
- [ ] `my_app/permissions.py` - New RBAC classes
- [ ] `my_app/urls.py` - New auth endpoints
- [ ] `calmspcae_backend/settings.py` - Email & JWT config

**Documentation Files:**

- [ ] `AUTHENTICATION_GUIDE.md`
- [ ] `TESTING_GUIDE.md`
- [ ] `IMPLEMENTATION_SUMMARY.md`
- [ ] `FEATURES_OVERVIEW.md`
- [ ] `CalmSpace_API.postman_collection.json`
- [ ] `.env.example`

### Phase 5: Code Quality ✓

- [ ] Run linter: `python -m flake8 my_app/`
- [ ] Check imports in all files
- [ ] Verify no hardcoded credentials
- [ ] Check for security issues
- [ ] Verify error handling
- [ ] Check for deprecated functions

### Phase 6: Security Validation ✓

- [ ] Verify `SECRET_KEY` not in code
- [ ] Verify password fields never returned in responses
- [ ] Verify tokens expire correctly
- [ ] Verify one-time token usage
- [ ] Verify CORS configuration
- [ ] Verify CSRF protection
- [ ] Check SSL/HTTPS readiness

### Phase 7: Testing - Registration Flow ✓

- [ ] Test register with valid data

  - [ ] User created in database
  - [ ] Email sent to inbox
  - [ ] Token generated
  - [ ] User `is_email_verified` = False

- [ ] Test register with invalid email

  - [ ] Returns 400 error
  - [ ] Proper error message

- [ ] Test register with duplicate email

  - [ ] Returns 400 error
  - [ ] "Email already exists" message

- [ ] Test register with weak password

  - [ ] Returns 400 error
  - [ ] Password strength message

- [ ] Test register with mismatched passwords
  - [ ] Returns 400 error
  - [ ] "Passwords don't match" message

### Phase 8: Testing - Email Verification ✓

- [ ] Email received within 1 minute
- [ ] Email contains verification link
- [ ] Link has correct token and uid
- [ ] Link opens in frontend
- [ ] Click verify button on frontend
- [ ] Token validated on backend
- [ ] User `is_email_verified` updated to True
- [ ] Token marked as used

- [ ] Test verify with invalid token

  - [ ] Returns 400 error
  - [ ] "Invalid token" message

- [ ] Test verify with expired token

  - [ ] Returns 400 error
  - [ ] "Token expired" message

- [ ] Test resend verification email
  - [ ] New email sent
  - [ ] New token generated
  - [ ] Old token still valid

### Phase 9: Testing - Login Flow ✓

- [ ] Login before email verification

  - [ ] Returns 400 error
  - [ ] "Email not verified" message

- [ ] Login after email verification

  - [ ] Returns 200 OK
  - [ ] Access token returned
  - [ ] Refresh token returned
  - [ ] User data returned

- [ ] Login with wrong password

  - [ ] Returns 400 error
  - [ ] "Invalid credentials" message

- [ ] Login with non-existent email
  - [ ] Returns 400 error
  - [ ] "User not found" message

### Phase 10: Testing - Password Reset Flow ✓

- [ ] Request password reset (forgot password)

  - [ ] Returns 200 OK
  - [ ] Email sent to user
  - [ ] Token generated

- [ ] Password reset email received

  - [ ] Email contains reset link
  - [ ] Link has correct token and uid

- [ ] Click reset password link

  - [ ] Opens reset form in frontend
  - [ ] Submit new password
  - [ ] Token validated

- [ ] Reset password successful

  - [ ] Returns 200 OK
  - [ ] Token marked as used
  - [ ] Password updated in database
  - [ ] "Password reset successful" message

- [ ] Test reset with invalid token

  - [ ] Returns 400 error
  - [ ] "Invalid token" message

- [ ] Test reset with mismatched passwords

  - [ ] Returns 400 error
  - [ ] "Passwords don't match" message

- [ ] Login with new password
  - [ ] Returns 200 OK
  - [ ] Successfully logged in

### Phase 11: Testing - Profile Management ✓

- [ ] Get profile without auth token

  - [ ] Returns 401 Unauthorized

- [ ] Get profile with valid token

  - [ ] Returns 200 OK
  - [ ] User data returned
  - [ ] No sensitive data exposed

- [ ] Update profile (name only)

  - [ ] Name updated in database
  - [ ] Other fields unchanged
  - [ ] Returns updated user

- [ ] Update profile (with image)

  - [ ] Image uploaded to media folder
  - [ ] Image path stored in database
  - [ ] Image accessible via URL

- [ ] Change password (authenticated user)

  - [ ] Old password verified
  - [ ] New password set
  - [ ] Returns 200 OK
  - [ ] Can login with new password

- [ ] Change password with wrong old password
  - [ ] Returns 400 error
  - [ ] "Old password incorrect" message

### Phase 12: Testing - Role-Based Access ✓

**Create test users:**

- [ ] Create admin user
- [ ] Create staff user
- [ ] Create customer user
- [ ] Create therapist user

**Test Admin Access:**

- [ ] Admin can access admin-only endpoint
- [ ] Staff cannot access admin endpoint
- [ ] Customer cannot access admin endpoint

**Test Staff Access:**

- [ ] Staff can access staff endpoint
- [ ] Customer cannot access staff endpoint
- [ ] Admin can access staff endpoint

**Test Customer Access:**

- [ ] Customer can access customer endpoint
- [ ] Customer can access their own data
- [ ] Customer cannot access other users' data

**Test Email Verification Requirement:**

- [ ] Unverified user cannot access protected routes
- [ ] Verified user can access protected routes

### Phase 13: Testing - Error Handling ✓

- [ ] 400 errors have proper messages
- [ ] 401 errors for missing auth
- [ ] 403 errors for unauthorized access
- [ ] 404 errors for non-existent resources
- [ ] 500 errors logged properly
- [ ] All error responses include `success: false`

### Phase 14: Testing - Database Integrity ✓

- [ ] Check user table has all required fields
- [ ] Check email verification token table
- [ ] Check password reset token table
- [ ] Check groups created (4 total)
- [ ] Check group permissions assigned
- [ ] Verify no orphaned tokens
- [ ] Verify referential integrity

### Phase 15: Performance Testing ✓

- [ ] Register multiple users simultaneously (10+)

  - [ ] No race conditions
  - [ ] All emails sent
  - [ ] All tokens unique

- [ ] Concurrent login requests

  - [ ] All requests handled
  - [ ] All tokens valid
  - [ ] No token collision

- [ ] Database query performance
  - [ ] Profile query < 100ms
  - [ ] Login query < 100ms
  - [ ] Permission check < 50ms

### Phase 16: Security Testing ✓

- [ ] SQL injection in email field

  - [ ] No bypassing validation
  - [ ] Error returned

- [ ] SQL injection in password field

  - [ ] No bypassing validation
  - [ ] Error returned

- [ ] Cross-site scripting (XSS)

  - [ ] No script execution
  - [ ] Input sanitized

- [ ] CSRF attack prevention

  - [ ] CSRF token checked
  - [ ] Attacks blocked

- [ ] Token replay attack

  - [ ] Tokens expire
  - [ ] Used tokens rejected
  - [ ] Cannot reuse reset tokens

- [ ] Password exposure
  - [ ] Password never in logs
  - [ ] Password never in response
  - [ ] Password properly hashed

### Phase 17: Frontend Integration Testing ✓

- [ ] Frontend can register user
- [ ] Frontend receives verification link
- [ ] Frontend can verify email
- [ ] Frontend can login
- [ ] Frontend stores JWT token correctly
- [ ] Frontend includes token in requests
- [ ] Frontend handles token expiration
- [ ] Frontend displays error messages
- [ ] Frontend can update profile
- [ ] Frontend can upload profile image
- [ ] Frontend can request password reset
- [ ] Frontend can reset password
- [ ] Frontend shows loading states
- [ ] Frontend shows success messages
- [ ] Frontend shows error messages

### Phase 18: Documentation Review ✓

- [ ] AUTHENTICATION_GUIDE.md complete and accurate
- [ ] TESTING_GUIDE.md complete and accurate
- [ ] IMPLEMENTATION_SUMMARY.md complete
- [ ] FEATURES_OVERVIEW.md complete
- [ ] API endpoints documented
- [ ] Error codes documented
- [ ] Examples working
- [ ] Frontend integration guide clear

### Phase 19: Postman Collection ✓

- [ ] Import collection into Postman
- [ ] All endpoints accessible
- [ ] Token variables work
- [ ] Register endpoint works
- [ ] Login endpoint works
- [ ] Verify email endpoint works
- [ ] Password reset endpoints work
- [ ] Profile endpoints work
- [ ] Error scenarios work

### Phase 20: Production Readiness ✓

- [ ] Set `DEBUG=False` in production settings
- [ ] Review `ALLOWED_HOSTS` configuration
- [ ] Review `CORS_ALLOWED_ORIGINS`
- [ ] Configure email service (Gmail/SendGrid/AWS SES)
- [ ] Setup HTTPS/SSL certificates
- [ ] Configure database backups
- [ ] Setup error logging (Sentry/etc)
- [ ] Setup monitoring (Datadog/NewRelic/etc)
- [ ] Review SECRET_KEY rotation
- [ ] Plan database migration strategy

---

## Testing Reports Template

### Registration Testing Report

```
Date: [DATE]
Tester: [NAME]
Environment: [DEV/STAGING/PRODUCTION]

✓ Successful registrations: [COUNT]
✓ Email verification: [PASS/FAIL]
✓ Error handling: [PASS/FAIL]
✓ Performance: [PASS/FAIL]

Issues found:
- [ISSUE 1]
- [ISSUE 2]

Notes:
[ADDITIONAL NOTES]
```

### Login Testing Report

```
Date: [DATE]
Tester: [NAME]

✓ Successful logins: [COUNT]
✓ JWT tokens valid: [PASS/FAIL]
✓ Permission checks: [PASS/FAIL]
✓ Error handling: [PASS/FAIL]

Issues found:
- [ISSUE 1]

Notes:
[ADDITIONAL NOTES]
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Security audit completed
- [ ] Performance tested
- [ ] Documentation updated
- [ ] Backup created

### Deployment

- [ ] Deploy code to server
- [ ] Run migrations on production
- [ ] Collect static files
- [ ] Restart application server
- [ ] Verify all endpoints working
- [ ] Monitor error logs

### Post-Deployment

- [ ] Monitor for errors (first 1 hour)
- [ ] Check database size
- [ ] Verify backups working
- [ ] Send notification to team
- [ ] Document any issues
- [ ] Plan follow-up improvements

---

## Rollback Plan

If deployment fails:

1. [ ] Restore database from backup
2. [ ] Revert code to previous version
3. [ ] Clear cache
4. [ ] Restart servers
5. [ ] Verify system working
6. [ ] Notify team
7. [ ] Plan fixes

---

## Sign-Off

| Role            | Name | Date | Signature |
| --------------- | ---- | ---- | --------- |
| Developer       |      |      |           |
| QA Lead         |      |      |           |
| DevOps          |      |      |           |
| Project Manager |      |      |           |

---

**Status:** Ready for Testing ✅

**Estimated Testing Time:** 2-3 days

**Estimated Deployment Time:** 1-2 hours
