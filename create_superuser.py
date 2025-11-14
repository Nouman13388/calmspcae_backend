#!/usr/bin/env python
"""Create superuser script for development"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmspcae_backend.settings')
django.setup()

from my_app.models import User

# Create superuser if doesn't exist
if not User.objects.filter(email='admin@test.com').exists():
    user = User.objects.create_superuser(
        email='admin@test.com',
        name='Admin User',
        password='admin123'
    )
    user.is_email_verified = True
    user.user_type = 'admin'
    user.save()
    print("✓ Superuser created successfully!")
    print("  Email: admin@test.com")
    print("  Password: admin123")
    print("  User Type: admin")
else:
    print("✓ Superuser already exists")
    print("  Email: admin@test.com")
