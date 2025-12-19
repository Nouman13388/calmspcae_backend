"""
RevenueCat Subscription Models for CalmSpace
Handles subscription tracking and entitlements for premium features.
"""

from django.db import models
from django.utils import timezone
from .models import User


class SubscriptionPlan(models.Model):
    """
    Defines available subscription plans that map to RevenueCat products.
    """
    PLAN_TYPE_CHOICES = (
        ('free', 'Free'),
        ('monthly', 'Monthly Premium'),
        ('yearly', 'Yearly Premium'),
        ('lifetime', 'Lifetime Premium'),
    )

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, unique=True)
    revenuecat_product_id = models.CharField(max_length=255, unique=True, help_text="Product ID in RevenueCat")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    description = models.TextField(blank=True)
    
    # Features included in this plan
    unlimited_appointments = models.BooleanField(default=False)
    premium_therapists = models.BooleanField(default=False)
    unlimited_chat = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    exclusive_content = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_plan_table'
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}"


class UserSubscription(models.Model):
    """
    Tracks user subscription status synced with RevenueCat.
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('grace_period', 'Grace Period'),
        ('paused', 'Paused'),
        ('trial', 'Trial'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    
    # RevenueCat identifiers
    revenuecat_app_user_id = models.CharField(max_length=255, unique=True, help_text="RevenueCat App User ID")
    revenuecat_customer_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Subscription status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='expired')
    is_premium = models.BooleanField(default=False)
    
    # Dates
    original_purchase_date = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    unsubscribe_detected_at = models.DateTimeField(null=True, blank=True)
    billing_issue_detected_at = models.DateTimeField(null=True, blank=True)
    
    # Store information
    store = models.CharField(max_length=50, blank=True, null=True, help_text="app_store, play_store, stripe, etc.")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_subscription_table'

    def __str__(self):
        return f"{self.user.email} - {self.status}"

    def is_active_subscription(self):
        """Check if user has an active subscription."""
        if self.status in ['active', 'grace_period', 'trial']:
            if self.expires_at is None or self.expires_at > timezone.now():
                return True
        return False

    def has_feature(self, feature_name):
        """Check if the current subscription includes a specific feature."""
        if not self.is_active_subscription() or not self.plan:
            return False
        return getattr(self.plan, feature_name, False)


class SubscriptionTransaction(models.Model):
    """
    Records individual subscription transactions/events from RevenueCat webhooks.
    """
    EVENT_TYPE_CHOICES = (
        ('INITIAL_PURCHASE', 'Initial Purchase'),
        ('RENEWAL', 'Renewal'),
        ('CANCELLATION', 'Cancellation'),
        ('UNCANCELLATION', 'Uncancellation'),
        ('EXPIRATION', 'Expiration'),
        ('BILLING_ISSUE', 'Billing Issue'),
        ('PRODUCT_CHANGE', 'Product Change'),
        ('TRANSFER', 'Transfer'),
        ('REFUND', 'Refund'),
    )

    user_subscription = models.ForeignKey(
        UserSubscription, 
        on_delete=models.CASCADE, 
        related_name='transactions',
        null=True,
        blank=True
    )
    
    # Transaction details
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True)
    original_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Product info
    product_id = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    
    # Dates
    purchased_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Store
    store = models.CharField(max_length=50, blank=True, null=True)
    
    # Raw webhook payload for debugging
    raw_payload = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscription_transaction_table'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} - {self.transaction_id}"


class Entitlement(models.Model):
    """
    Maps RevenueCat entitlements to features in the app.
    """
    name = models.CharField(max_length=100, unique=True)
    revenuecat_entitlement_id = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'entitlement_table'

    def __str__(self):
        return self.name


class UserEntitlement(models.Model):
    """
    Tracks which entitlements a user currently has access to.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entitlements')
    entitlement = models.ForeignKey(Entitlement, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_entitlement_table'
        unique_together = ['user', 'entitlement']

    def __str__(self):
        return f"{self.user.email} - {self.entitlement.name}"
