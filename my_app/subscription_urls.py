"""
URL patterns for RevenueCat Subscription Management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .subscription_views import (
    SubscriptionPlanViewSet,
    UserSubscriptionViewSet,
    SubscriptionTransactionViewSet,
    EntitlementViewSet,
    UserEntitlementViewSet,
    grant_promotional_access,
    revoke_promotional_access,
    revenuecat_webhook,
    check_feature_access,
)

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet, basename='subscription-plans')
router.register(r'user-subscriptions', UserSubscriptionViewSet, basename='user-subscriptions')
router.register(r'transactions', SubscriptionTransactionViewSet, basename='subscription-transactions')
router.register(r'entitlements', EntitlementViewSet, basename='entitlements')
router.register(r'user-entitlements', UserEntitlementViewSet, basename='user-entitlements')

urlpatterns = [
    path('', include(router.urls)),
    
    # Custom endpoints
    path('grant-promotional/', grant_promotional_access, name='grant-promotional'),
    path('revoke-promotional/', revoke_promotional_access, name='revoke-promotional'),
    path('check-feature/', check_feature_access, name='check-feature'),
    
    # Webhook endpoint
    path('webhook/revenuecat/', revenuecat_webhook, name='revenuecat-webhook'),
]
