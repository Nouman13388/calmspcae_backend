# Quick Start Guide - CalmSpace Backend

**Status:** ✅ Running and Ready  
**URL:** http://localhost:8000  
**API:** http://localhost:8000/api

---

## 🚀 Get Started in 2 Minutes

### 1. Activate Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Start the Server

```bash
python manage.py runserver
```

Server will start at: `http://localhost:8000`

### 3. Test Login

```bash
# Use Postman or curl
POST http://localhost:8000/api/auth/login/

{
  "email": "admin@test.com",
  "password": "admin123"
}
```

You'll get JWT tokens back! 🎉

---

## 📚 Main Endpoints

### User Management

| Method | Endpoint                     | Description        |
| ------ | ---------------------------- | ------------------ |
| POST   | `/api/auth/register/`        | Create new account |
| POST   | `/api/auth/login/`           | Login & get tokens |
| GET    | `/api/auth/profile/`         | Get your profile   |
| PUT    | `/api/auth/update-profile/`  | Update profile     |
| POST   | `/api/auth/change-password/` | Change password    |

### Password Reset

| Method | Endpoint                     | Description         |
| ------ | ---------------------------- | ------------------- |
| POST   | `/api/auth/forgot-password/` | Request reset email |
| POST   | `/api/auth/reset-password/`  | Set new password    |

### Email Verification

| Method | Endpoint                               | Description         |
| ------ | -------------------------------------- | ------------------- |
| POST   | `/api/auth/verify-email/`              | Verify email token  |
| POST   | `/api/auth/resend-verification-email/` | Resend verification |

---

## 🧪 Test It Now

### Option 1: Use Postman

1. Open Postman
2. Import: `CalmSpace_API.postman_collection.json`
3. Run requests!

### Option 2: Use Script

```powershell
# Windows
cmd /c test_api.bat

# Or PowerShell
.\test_api_simple.ps1
```

### Option 3: Use cURL

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}'
```

---

## 🔑 Test Account

```
Email: admin@test.com
Password: admin123
Role: Admin
```

---

## 📖 Documentation

- **API Reference** → `AUTHENTICATION_GUIDE.md`
- **Testing Guide** → `TESTING_GUIDE.md`
- **Features** → `FEATURES_OVERVIEW.md`
- **Deployment** → `DEPLOYMENT_CHECKLIST.md`

---

## ⚙️ Configure (Optional)

### Setup Email (Gmail)

1. Edit `.env` file
2. Add your Gmail credentials:

```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

3. Get App Password from: https://support.google.com/accounts/answer/185833

### Create New Admin Account

```bash
python create_superuser.py
```

---

## 🆘 Troubleshooting

### Server won't start?

```bash
# Check for errors
python manage.py migrate

# Restart
python manage.py runserver
```

### Login returns 401?

- Verify email is correct
- Verify password is correct
- Try with admin@test.com / admin123

### API returns 403?

- Check if token is included in headers
- Token format: `Authorization: Bearer <token>`

---

## 🎯 What to Try

1. **Register a new user**

   ```json
   POST /api/auth/register/
   {
     "email": "newuser@test.com",
     "name": "New User",
     "phone_number": "1234567890",
     "user_type": "customer",
     "password": "SecurePass123!",
     "password_confirm": "SecurePass123!"
   }
   ```

2. **Login with that user**

   ```json
   POST /api/auth/login/
   {
     "email": "newuser@test.com",
     "password": "SecurePass123!"
   }
   ```

3. **Get your profile (use token from login)**

   ```
   GET /api/auth/profile/
   Header: Authorization: Bearer <access_token>
   ```

4. **Update your profile**
   ```json
   PUT /api/auth/update-profile/
   Header: Authorization: Bearer <access_token>
   {
     "name": "Updated Name",
     "phone_number": "9876543210"
   }
   ```

---

## 📊 Features Available

✅ Custom User Model  
✅ JWT Authentication  
✅ Email Verification  
✅ Password Reset  
✅ Role-Based Access Control  
✅ Profile Management  
✅ Image Upload  
✅ User Groups (Admin, Staff, Customer, Therapist)  
✅ Permission System  
✅ Error Handling

---

## 🚀 Next Steps

1. **Read the docs** - AUTHENTICATION_GUIDE.md
2. **Explore the API** - Use Postman collection
3. **Integrate frontend** - Use test account
4. **Configure email** - Update .env file
5. **Deploy** - Follow DEPLOYMENT_CHECKLIST.md

---

## 💬 API Response Examples

### Successful Login

```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "admin@test.com",
    "name": "Admin User",
    "phone_number": "+1234567890",
    "user_type": "admin",
    "is_email_verified": true
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Profile Response

```json
{
  "id": 1,
  "email": "admin@test.com",
  "name": "Admin User",
  "phone_number": "+1234567890",
  "profile_picture": null,
  "user_type": "admin",
  "is_email_verified": true,
  "created_at": "2025-11-14T06:38:56.133545Z"
}
```

---

## 🔐 Authentication

All endpoints except register/login require JWT token:

```
GET /api/auth/profile/ HTTP/1.1
Host: localhost:8000
Authorization: Bearer <access_token>
```

---

## 📞 Get Help

- Check documentation files (\*.md)
- Run test scripts
- Review API responses for error messages
- Check server console for errors

---

**Ready to go? Start the server and make your first API call!** 🚀

```bash
python manage.py runserver
```

Visit: http://localhost:8000/api
