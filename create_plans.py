"""
Script to create default subscription plans
Run with: python create_plans.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calmspcae_backend.settings')
django.setup()

from my_app.subscription_models import SubscriptionPlan

plans = [
    {
        'name': 'Free',
        'plan_type': 'free',
        'revenuecat_product_id': 'com.calmspace.free',
        'price': 0.00,
        'description': 'Basic access to CalmSpace features',
        'unlimited_appointments': False,
        'premium_therapists': False,
        'unlimited_chat': False,
        'priority_support': False,
        'exclusive_content': False,
    },
    {
        'name': 'Premium Monthly',
        'plan_type': 'monthly',
        'revenuecat_product_id': 'com.calmspace.premium_monthly',
        'price': 9.99,
        'description': 'Full access to all premium features, billed monthly',
        'unlimited_appointments': True,
        'premium_therapists': True,
        'unlimited_chat': True,
        'priority_support': True,
        'exclusive_content': True,
    },
    {
        'name': 'Premium Yearly',
        'plan_type': 'yearly',
        'revenuecat_product_id': 'com.calmspace.premium_yearly',
        'price': 79.99,
        'description': 'Full access to all premium features, billed yearly (save 33%)',
        'unlimited_appointments': True,
        'premium_therapists': True,
        'unlimited_chat': True,
        'priority_support': True,
        'exclusive_content': True,
    },
    {
        'name': 'Lifetime Premium',
        'plan_type': 'lifetime',
        'revenuecat_product_id': 'com.calmspace.premium_lifetime',
        'price': 199.99,
        'description': 'One-time payment for lifetime access to all premium features',
        'unlimited_appointments': True,
        'premium_therapists': True,
        'unlimited_chat': True,
        'priority_support': True,
        'exclusive_content': True,
    },
]

if __name__ == '__main__':
    print("Creating subscription plans...")
    for plan_data in plans:
        plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type=plan_data['plan_type'],
            defaults=plan_data
        )
        status_text = 'Created' if created else 'Already exists'
        print(f'  {status_text}: {plan.name} - ${plan.price}')

    print('\nDone! Plans are ready.')
    print(f'Total plans: {SubscriptionPlan.objects.count()}')
