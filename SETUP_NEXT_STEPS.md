# CalmSpace Backend Setup Guide

## ⚙️ NEXT STEPS FOR DEPLOYMENT

### Step 1: Install MySQL Driver (For Windows + Python 3.13)

Since you're on Windows with Python 3.13, mysqlclient has compatibility issues. Use this alternative:

```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Install mysql-connector-python instead
pip install mysql-connector-python
```

Then update your `requirements.txt`:

```diff
- mysqlclient==2.2.4
+ mysql-connector-python==9.0.0
```

### Step 2: Update Database Settings

If you want to use SQLite for development (easier on Windows), update your `.env`:

```
DATABASE_ENGINE=sqlite3
DATABASE_NAME=db.sqlite3
```

Or for MySQL, ensure these are in your `.env`:

```
DATABASE_ENGINE=mysql
DATABASE_NAME=calmspace
DATABASE_USER=root
DATABASE_PASSWORD=admin
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

### Step 3: Create/Update .env File

Copy `.env.example` and create `.env`:

```bash
# Database
DATABASE_NAME=calmspace
DATABASE_USER=root
DATABASE_PASSWORD=admin
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Email Configuration (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# JWT & Tokens
SECRET_KEY=your-secret-key-here
DEBUG=True

# Token Expiry (in seconds)
EMAIL_VERIFICATION_TOKEN_EXPIRY=86400
PASSWORD_RESET_TOKEN_EXPIRY=86400
```

### Step 4: Run Migrations

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Step 5: Create User Groups

```bash
python manage.py setup_user_groups
```

### Step 6: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 7: Test the Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

---

## 🐛 TROUBLESHOOTING

### Issue: MySQLdb ImportError on Windows

**Solution:** Use `mysql-connector-python` instead

```bash
pip uninstall mysqlclient -y
pip install mysql-connector-python
```

Then update settings to use the connector:

```python
DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD', default=''),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default=3306, cast=int),
    }
}
```

### Issue: MySQL Connection Refused

**Solutions:**

1. Ensure MySQL server is running
2. Check DATABASE_HOST, DATABASE_USER, PASSWORD are correct
3. Verify database exists: `CREATE DATABASE IF NOT EXISTS calmspace;`

### Issue: Email Not Sending

**Solutions:**

1. Enable 2FA on Gmail
2. Create App Password: https://support.google.com/accounts/answer/185833
3. Use App Password in EMAIL_HOST_PASSWORD
4. Try test command: `python manage.py shell` then:
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Message', 'from@gmail.com', ['to@gmail.com'])
   ```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list | grep -i django`)
- [ ] .env file created
- [ ] Database configured (MySQL or SQLite)
- [ ] Migrations created (`python manage.py makemigrations`)
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] User groups created (`python manage.py setup_user_groups`)
- [ ] Server starts (`python manage.py runserver`)
- [ ] API accessible (http://localhost:8000/api/)

---

## 🎯 QUICK START COMMANDS

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Install mysql connector (if using MySQL)
pip install mysql-connector-python

# Create .env from example
cp .env.example .env

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Setup groups
python manage.py setup_user_groups

# Start server
python manage.py runserver
```

---

## 📞 SUPPORT RESOURCES

- **Authentication Guide:** See `AUTHENTICATION_GUIDE.md`
- **Testing Guide:** See `TESTING_GUIDE.md`
- **Deployment Checklist:** See `DEPLOYMENT_CHECKLIST.md`
- **API Documentation:** See `README_IMPLEMENTATION.md`

---

**Status:** Ready for Setup ✅
**Last Updated:** November 14, 2025
