"""
Serializers for RevenueCat Subscription Management
"""

from rest_framework import serializers
from .subscription_models import (
    SubscriptionPlan, 
    UserSubscription, 
    SubscriptionTransaction,
    Entitlement,
    UserEntitlement
)


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans."""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'revenuecat_product_id',
            'price', 'currency', 'description',
            'unlimited_appointments', 'premium_therapists',
            'unlimited_chat', 'priority_support', 'exclusive_content',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscription status."""
    
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'user_email', 'plan', 'plan_details',
            'revenuecat_app_user_id', 'status', 'is_premium',
            'original_purchase_date', 'expires_at',
            'unsubscribe_detected_at', 'billing_issue_detected_at',
            'store', 'is_active', 'last_synced_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'plan_details', 'is_active',
            'created_at', 'updated_at'
        ]

    def get_is_active(self, obj):
        return obj.is_active_subscription()


class SubscriptionTransactionSerializer(serializers.ModelSerializer):
    """Serializer for subscription transactions."""
    
    class Meta:
        model = SubscriptionTransaction
        fields = [
            'id', 'user_subscription', 'event_type', 'transaction_id',
            'original_transaction_id', 'product_id', 'price', 'currency',
            'purchased_at', 'expires_at', 'store', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EntitlementSerializer(serializers.ModelSerializer):
    """Serializer for entitlements."""
    
    class Meta:
        model = Entitlement
        fields = ['id', 'name', 'revenuecat_entitlement_id', 'description', 'is_active']
        read_only_fields = ['id']


class UserEntitlementSerializer(serializers.ModelSerializer):
    """Serializer for user entitlements."""
    
    entitlement_details = EntitlementSerializer(source='entitlement', read_only=True)
    
    class Meta:
        model = UserEntitlement
        fields = ['id', 'user', 'entitlement', 'entitlement_details', 'is_active', 'expires_at']
        read_only_fields = ['id']


class SubscriptionStatusSerializer(serializers.Serializer):
    """Serializer for quick subscription status check."""
    
    is_premium = serializers.BooleanField()
    status = serializers.CharField()
    plan_name = serializers.CharField(allow_null=True)
    expires_at = serializers.DateTimeField(allow_null=True)
    features = serializers.DictField()


class RevenueCatWebhookSerializer(serializers.Serializer):
    """Serializer for RevenueCat webhook payloads."""
    
    api_version = serializers.CharField(required=False)
    event = serializers.DictField()
    
    def validate_event(self, value):
        required_fields = ['type', 'app_user_id']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")
        return value


class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer for creating/linking RevenueCat subscription."""
    
    revenuecat_app_user_id = serializers.CharField(max_length=255)
    
    def validate_revenuecat_app_user_id(self, value):
        if not value or len(value) < 1:
            raise serializers.ValidationError("RevenueCat App User ID is required")
        return value


class SyncSubscriptionSerializer(serializers.Serializer):
    """Serializer for syncing subscription from RevenueCat."""
    
    force_refresh = serializers.BooleanField(default=False, required=False)
