# CalmSpace Backend

Django REST API with JWT authentication, email verification, password reset, and role-based access control.

## Quick Start

### 1. Setup

```powershell
# Clone and navigate
git clone <repo-url>
cd calmspcae_backend

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

Create `.env` file:

```
DATABASE_ENGINE=sqlite
DEBUG=True
SECRET_KEY=your-secret-key-here
IS_PRODUCTION=False
```

### 3. Initialize Database

```powershell
python manage.py migrate
python manage.py setup_user_groups
python create_superuser.py
```

### 4. Run Server

```powershell
python manage.py runserver
```

## Access Points

- **API**: http://127.0.0.1:8000/api/
- **Dashboard**: http://127.0.0.1:8000/dashboard/
- **Admin**: http://127.0.0.1:8000/admin/

## Test Account

```
Email: admin@test.com
Password: admin123
```

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/verify-email/` - Verify email with token
- `POST /api/auth/resend-verification-email/` - Resend verification

### Profile Management (requires authentication)

- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/update-profile/` - Update profile
- `POST /api/auth/change-password/` - Change password

### Password Reset

- `POST /api/auth/forgot-password/` - Request reset email
- `POST /api/auth/reset-password/` - Reset with token

## Features

- Custom User model with email authentication
- JWT token-based authentication
- Email verification system
- Password reset functionality
- Role-based access control (Admin, Staff, Customer, Therapist)
- Profile management with image upload
- Interactive API dashboard

## Tech Stack

- Django 5.1.1
- Django REST Framework 3.15.2
- djangorestframework-simplejwt 5.3.1
- Python 3.13+
- SQLite (dev) / MySQL (prod)

## Documentation

- API testing with Postman: Import `CalmSpace_API.postman_collection.json`
- Full API docs: `AUTHENTICATION_GUIDE.md`
- Testing guide: `TESTING_GUIDE.md`

## Notes about Channels (WebSockets)

- In development (`DEBUG=True`) the project uses the in-memory channel layer, which is not suitable for production but allows WebSocket features while developing without Redis.
- In production, ensure you have Redis running and update `CHANNEL_LAYERS` settings or set `DEBUG=False` and configure the Redis host/port as needed.

## Static files

- `STATICFILES_DIRS` points to a `static/` directory at the project root. Create that directory if you plan to serve or collect static files locally:

```powershell
New-Item -ItemType Directory -Path .\static
```

## Troubleshooting

- mysqlclient installation fails on Windows: Use `requirements-dev.txt` (it excludes `mysqlclient`) or install prebuilt wheels for your Python version. If you need MySQL locally, consider using WSL or a Docker container.
- Redis not available: development will use an in-memory channel layer. For production, install Redis and configure `CHANNEL_LAYERS` accordingly.
- Static files warning: create the `static/` folder or change `STATICFILES_DIRS` in `settings.py`.

## Project structure (top-level)

- manage.py
- requirements.txt (full dependencies)
- requirements-dev.txt (dev-friendly, excludes mysqlclient)
- calmspcae_backend/ (Django project package)
- my_app/ (application code)
- media/ (uploaded files)

## Security

- Do NOT commit real secret keys or production credentials. Keep `.env` out of version control. The repo currently expects a `.env` file for configuration via `django-environ` and `python-decouple`.

## Next steps you might want

- Add `requirements-dev.txt` to the repo (already created) and commit it.
- Update `README.md` with API endpoints and authentication details once you finalize the API surface.
- Add Docker support for reproducing the exact prod environment locally (MySQL/Redis) if needed.

If you'd like, I can:

- Commit `requirements-dev.txt` and `README.md` changes and create a small `README` PR.
- Add a `make` or PowerShell script to automate venv creation and run steps.
- Add a `CONTRIBUTING.md` with setup notes for new devs.
