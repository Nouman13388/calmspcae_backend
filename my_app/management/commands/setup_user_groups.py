"""
Management command to setup user groups and permissions
Run with: python manage.py setup_user_groups
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Setup user groups and permissions for role-based access control'

    def handle(self, *args, **options):
        # Create groups
        admin_group, created = Group.objects.get_or_create(name='Admin')
        staff_group, created = Group.objects.get_or_create(name='Staff')
        customer_group, created = Group.objects.get_or_create(name='Customer')
        therapist_group, created = Group.objects.get_or_create(name='Therapist')

        # Get all permissions
        all_permissions = Permission.objects.all()

        # Admin group - full access
        admin_group.permissions.set(all_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Admin group created with all permissions'))

        # Staff group - limited access
        staff_permissions = Permission.objects.filter(
            codename__in=[
                'view_user', 'change_user',
                'view_profile', 'add_profile', 'change_profile', 'delete_profile',
                'view_assessment', 'add_assessment', 'change_assessment',
                'view_healthdata', 'add_healthdata', 'change_healthdata',
                'view_feedback', 'add_feedback',
                'view_appointment', 'add_appointment', 'change_appointment',
                'view_clinic', 'add_clinic', 'change_clinic',
                'view_article', 'add_article', 'change_article',
            ]
        )
        staff_group.permissions.set(staff_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Staff group created with limited permissions'))

        # Customer group - basic access
        customer_permissions = Permission.objects.filter(
            codename__in=[
                'view_user', 'change_user',
                'view_profile', 'add_profile', 'change_profile',
                'view_assessment', 'add_assessment',
                'view_healthdata', 'add_healthdata', 'change_healthdata',
                'add_feedback',
                'view_appointment', 'add_appointment',
                'view_clinic',
                'view_article',
            ]
        )
        customer_group.permissions.set(customer_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Customer group created with basic permissions'))

        # Therapist group
        therapist_permissions = Permission.objects.filter(
            codename__in=[
                'view_user', 'change_user',
                'view_profile',
                'view_assessment', 'add_assessment', 'change_assessment',
                'view_healthdata',
                'view_feedback', 'add_feedback',
                'view_appointment', 'change_appointment',
                'view_clinic',
                'view_article', 'add_article', 'change_article',
            ]
        )
        therapist_group.permissions.set(therapist_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Therapist group created with therapist permissions'))

        self.stdout.write(self.style.SUCCESS('✓ All user groups and permissions have been created successfully!'))
