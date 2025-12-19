from pathlib import Path
from decouple import config
import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()  # Reads the .env file if available

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
IS_PRODUCTION = config('IS_PRODUCTION', default=False, cast=bool)
DEBUG = not IS_PRODUCTION  # Set DEBUG to True only in development

ALLOWED_HOSTS = [
    '50.19.24.133', '16.171.9.75', '127.0.0.1', 'localhost', '.vercel.app', '.now.sh'
]  # Add more hosts as needed

# Media files (uploads)
MEDIA_URL = '/media/'  # URL path for serving media files
MEDIA_ROOT = BASE_DIR / 'media'  # Local directory where media files are stored

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'  # URL path for serving static files
STATICFILES_DIRS = [BASE_DIR / 'static']  # Directories where static files are stored
STATIC_ROOT = BASE_DIR / 'staticfiles_build' / 'static'  # Output directory for static files in production

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'my_app',  # Replace with the correct app name
    'channels',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'sslserver',  # Use this only if needed for local HTTPS
]

# Custom User Model
AUTH_USER_MODEL = 'my_app.User'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = not IS_PRODUCTION  # Allow all origins in development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend development URL
    "https://your-production-domain.com",  # Replace with actual production domain
    "http://172.17.239.232:8000",  # Another example URL
]

# Security settings
SECURE_SSL_REDIRECT = IS_PRODUCTION  # Enable SSL redirection in production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # One year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
CSRF_TRUSTED_ORIGINS = [
    "https://your-production-domain.com",  # Add your production domain here
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ASGI_APPLICATION = 'core.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('50.19.24.133', 6379)],
        },
    },
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Ensure CORS is placed correctly
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'calmspcae_backend.urls'  # Updated project name

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database configuration (using django-environ for flexibility)
# Support both SQLite (development) and MySQL (production)
DATABASE_ENGINE = config('DATABASE_ENGINE', default='mysql')

if DATABASE_ENGINE == 'sqlite':
    # SQLite configuration for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # MySQL configuration for production
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DATABASE_NAME', default='calmspace'),
            'USER': config('DATABASE_USER', default='root'),
            'PASSWORD': config('DATABASE_PASSWORD', default=''),
            'HOST': config('DATABASE_HOST', default='localhost'),
            'PORT': config('DATABASE_PORT', default=3306, cast=int),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# Token Expiration (in seconds)
EMAIL_VERIFICATION_TOKEN_EXPIRY = 24 * 60 * 60  # 24 hours
PASSWORD_RESET_TOKEN_EXPIRY = 24 * 60 * 60  # 24 hours

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}

# Print database connection information (for debugging, can be removed in production)
if DEBUG:
    print("Database Name:", config('DATABASE_NAME'))
    print("Database User:", config('DATABASE_USER'))
    print("Database Password:", config('DATABASE_PASSWORD'))
    print("Database Host:", config('DATABASE_HOST'))
    print("Database Port:", config('DATABASE_PORT'))

# RevenueCat Configuration
REVENUECAT_API_KEY = config('REVENUECAT_API_KEY', default='')
REVENUECAT_WEBHOOK_SECRET = config('REVENUECAT_WEBHOOK_SECRET', default='')
REVENUECAT_PROJECT_ID = config('REVENUECAT_PROJECT_ID', default='')
