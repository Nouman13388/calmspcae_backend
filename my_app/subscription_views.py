"""
Subscription Views for RevenueCat Integration
"""

import json
import logging
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import User
from .subscription_models import (
    SubscriptionPlan,
    UserSubscription,
    SubscriptionTransaction,
    Entitlement,
    UserEntitlement,
)
from .subscription_serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
    SubscriptionTransactionSerializer,
    EntitlementSerializer,
    UserEntitlementSerializer,
    SubscriptionStatusSerializer,
    RevenueCatWebhookSerializer,
    CreateSubscriptionSerializer,
    SyncSubscriptionSerializer,
)
from .revenuecat_service import revenuecat_service

logger = logging.getLogger(__name__)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving subscription plans.
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['plan_type']
    ordering_fields = ['price', 'name']


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user subscriptions.
    """
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'status', 'is_premium']
    search_fields = ['user__email', 'revenuecat_app_user_id']
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            return UserSubscription.objects.filter(user_id=user_id)
        return UserSubscription.objects.all()
    
    @action(detail=False, methods=['post'])
    def create_or_link(self, request):
        """
        Create or link a RevenueCat subscription for a user.
        """
        serializer = CreateSubscriptionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        revenuecat_app_user_id = serializer.validated_data['revenuecat_app_user_id']
        
        # Create subscriber in RevenueCat
        subscriber_data = revenuecat_service.create_subscriber(
            revenuecat_app_user_id,
            attributes={
                'email': user.email,
                'name': user.name,
                'user_id': str(user.id),
            }
        )
        
        # Create or update local subscription record
        subscription, created = UserSubscription.objects.update_or_create(
            user=user,
            defaults={
                'revenuecat_app_user_id': revenuecat_app_user_id,
                'last_synced_at': timezone.now(),
            }
        )
        
        # Sync subscription status if we got data from RevenueCat
        if subscriber_data:
            parsed_data = revenuecat_service.parse_subscriber_data(subscriber_data)
            subscription.is_premium = parsed_data['is_premium']
            subscription.status = parsed_data['status']
            subscription.expires_at = parsed_data['expires_at']
            subscription.original_purchase_date = parsed_data['original_purchase_date']
            subscription.save()
        
        return Response(
            UserSubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """
        Sync subscription status from RevenueCat for a user.
        """
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscription = UserSubscription.objects.get(user_id=user_id)
        except UserSubscription.DoesNotExist:
            return Response(
                {'error': 'No subscription found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Fetch from RevenueCat
        subscriber_data = revenuecat_service.get_subscriber(
            subscription.revenuecat_app_user_id
        )
        
        if not subscriber_data:
            return Response(
                {'error': 'Could not fetch subscription data from RevenueCat'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Parse and update
        parsed_data = revenuecat_service.parse_subscriber_data(subscriber_data)
        
        subscription.is_premium = parsed_data['is_premium']
        subscription.status = parsed_data['status']
        subscription.expires_at = parsed_data['expires_at']
        subscription.original_purchase_date = parsed_data['original_purchase_date']
        subscription.last_synced_at = timezone.now()
        subscription.save()
        
        return Response(UserSubscriptionSerializer(subscription).data)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Get quick subscription status for a user.
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscription = UserSubscription.objects.select_related('plan').get(user_id=user_id)
        except UserSubscription.DoesNotExist:
            # Return default free status
            return Response({
                'is_premium': False,
                'status': 'never_subscribed',
                'plan_name': None,
                'expires_at': None,
                'features': {
                    'unlimited_appointments': False,
                    'premium_therapists': False,
                    'unlimited_chat': False,
                    'priority_support': False,
                    'exclusive_content': False,
                }
            })
        
        features = {}
        if subscription.plan:
            features = {
                'unlimited_appointments': subscription.plan.unlimited_appointments,
                'premium_therapists': subscription.plan.premium_therapists,
                'unlimited_chat': subscription.plan.unlimited_chat,
                'priority_support': subscription.plan.priority_support,
                'exclusive_content': subscription.plan.exclusive_content,
            }
        else:
            features = {
                'unlimited_appointments': subscription.is_premium,
                'premium_therapists': subscription.is_premium,
                'unlimited_chat': subscription.is_premium,
                'priority_support': subscription.is_premium,
                'exclusive_content': subscription.is_premium,
            }
        
        return Response({
            'is_premium': subscription.is_active_subscription(),
            'status': subscription.status,
            'plan_name': subscription.plan.name if subscription.plan else None,
            'expires_at': subscription.expires_at,
            'features': features,
        })


class SubscriptionTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing subscription transactions (read-only).
    """
    queryset = SubscriptionTransaction.objects.all()
    serializer_class = SubscriptionTransactionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user_subscription', 'event_type', 'store']
    ordering_fields = ['created_at', 'purchased_at']
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            return SubscriptionTransaction.objects.filter(
                user_subscription__user_id=user_id
            )
        return SubscriptionTransaction.objects.all()


class EntitlementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing entitlements.
    """
    queryset = Entitlement.objects.filter(is_active=True)
    serializer_class = EntitlementSerializer
    permission_classes = [AllowAny]


class UserEntitlementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user entitlements.
    """
    queryset = UserEntitlement.objects.all()
    serializer_class = UserEntitlementSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'entitlement', 'is_active']
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            return UserEntitlement.objects.filter(user_id=user_id)
        return UserEntitlement.objects.all()


@api_view(['POST'])
@permission_classes([AllowAny])
def grant_promotional_access(request):
    """
    Grant promotional premium access to a user.
    Used for admin/testing purposes.
    Works locally without RevenueCat API in test mode.
    """
    user_id = request.data.get('user_id')
    duration = request.data.get('duration', 'monthly')
    entitlement_id = request.data.get('entitlement_id', 'premium')
    test_mode = request.data.get('test_mode', True)  # Default to test mode
    
    if not user_id:
        return Response(
            {'error': 'user_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        subscription = UserSubscription.objects.get(user_id=user_id)
    except UserSubscription.DoesNotExist:
        # Auto-create subscription if it doesn't exist
        try:
            user = User.objects.get(id=user_id)
            subscription = UserSubscription.objects.create(
                user=user,
                revenuecat_app_user_id=f"calmspace_{user.id}",
                status='expired'
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    # Calculate expiration based on duration
    duration_map = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30),
        'two_month': timedelta(days=60),
        'three_month': timedelta(days=90),
        'six_month': timedelta(days=180),
        'yearly': timedelta(days=365),
        'lifetime': timedelta(days=36500),  # 100 years
    }
    
    expires_delta = duration_map.get(duration, timedelta(days=30))
    expires_at = timezone.now() + expires_delta
    
    if test_mode:
        # Local test mode - update directly without RevenueCat API
        subscription.is_premium = True
        subscription.status = 'active'
        subscription.expires_at = expires_at
        subscription.original_purchase_date = timezone.now()
        subscription.store = 'test_mode'
        subscription.last_synced_at = timezone.now()
        subscription.save()
        
        # Try to assign a premium plan
        try:
            plan = SubscriptionPlan.objects.filter(
                plan_type__in=['monthly', 'yearly'],
                is_active=True
            ).first()
            if plan:
                subscription.plan = plan
                subscription.save()
        except:
            pass
        
        # Create a transaction record
        SubscriptionTransaction.objects.create(
            user_subscription=subscription,
            event_type='INITIAL_PURCHASE',
            transaction_id=f"test_promo_{timezone.now().timestamp()}",
            product_id=f"promo_{duration}",
            price=0.00,
            currency='USD',
            store='test_mode',
            purchased_at=timezone.now(),
            expires_at=expires_at,
            raw_payload={'test_mode': True, 'duration': duration}
        )
        
        return Response({
            'success': True,
            'message': f'Promotional {duration} access granted (test mode)',
            'subscription': UserSubscriptionSerializer(subscription).data
        })
    else:
        # Production mode - use RevenueCat API
        success = revenuecat_service.grant_promotional_entitlement(
            subscription.revenuecat_app_user_id,
            entitlement_id,
            duration
        )
        
        if success:
            subscriber_data = revenuecat_service.get_subscriber(
                subscription.revenuecat_app_user_id
            )
            if subscriber_data:
                parsed_data = revenuecat_service.parse_subscriber_data(subscriber_data)
                subscription.is_premium = parsed_data['is_premium']
                subscription.status = parsed_data['status']
                subscription.expires_at = parsed_data['expires_at']
                subscription.last_synced_at = timezone.now()
                subscription.save()
            
            return Response({
                'success': True,
                'message': f'Promotional {duration} access granted',
                'subscription': UserSubscriptionSerializer(subscription).data
            })
        else:
            return Response(
                {'error': 'Failed to grant promotional access via RevenueCat'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([AllowAny])
def revoke_promotional_access(request):
    """
    Revoke promotional premium access from a user.
    Works locally without RevenueCat API in test mode.
    """
    user_id = request.data.get('user_id')
    entitlement_id = request.data.get('entitlement_id', 'premium')
    test_mode = request.data.get('test_mode', True)  # Default to test mode
    
    if not user_id:
        return Response(
            {'error': 'user_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        subscription = UserSubscription.objects.get(user_id=user_id)
    except UserSubscription.DoesNotExist:
        return Response(
            {'error': 'User subscription not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if test_mode:
        # Local test mode - update directly
        subscription.is_premium = False
        subscription.status = 'expired'
        subscription.expires_at = timezone.now()
        subscription.plan = None
        subscription.last_synced_at = timezone.now()
        subscription.save()
        
        # Create a transaction record
        SubscriptionTransaction.objects.create(
            user_subscription=subscription,
            event_type='CANCELLATION',
            transaction_id=f"test_revoke_{timezone.now().timestamp()}",
            product_id='promo_revoked',
            store='test_mode',
            purchased_at=timezone.now(),
            raw_payload={'test_mode': True, 'action': 'revoke'}
        )
        
        return Response({
            'success': True,
            'message': 'Promotional access revoked (test mode)',
            'subscription': UserSubscriptionSerializer(subscription).data
        })
    else:
        # Production mode - use RevenueCat API
        success = revenuecat_service.revoke_promotional_entitlement(
            subscription.revenuecat_app_user_id,
            entitlement_id
        )
        
        if success:
            subscriber_data = revenuecat_service.get_subscriber(
                subscription.revenuecat_app_user_id
            )
            if subscriber_data:
                parsed_data = revenuecat_service.parse_subscriber_data(subscriber_data)
                subscription.is_premium = parsed_data['is_premium']
                subscription.status = parsed_data['status']
                subscription.expires_at = parsed_data['expires_at']
                subscription.last_synced_at = timezone.now()
                subscription.save()
            
            return Response({
                'success': True,
                'message': 'Promotional access revoked',
                'subscription': UserSubscriptionSerializer(subscription).data
            })
        else:
            return Response(
                {'error': 'Failed to revoke promotional access'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def revenuecat_webhook(request):
    """
    Handle RevenueCat webhook events.
    
    RevenueCat webhook documentation:
    https://www.revenuecat.com/docs/webhooks
    """
    # Verify signature (optional but recommended in production)
    signature = request.headers.get('X-RevenueCat-Signature', '')
    if not revenuecat_service.verify_webhook_signature(request.body, signature):
        logger.warning("Invalid webhook signature")
        return Response(
            {'error': 'Invalid signature'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return Response(
            {'error': 'Invalid JSON'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate payload
    serializer = RevenueCatWebhookSerializer(data=payload)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    event = payload.get('event', {})
    event_type = event.get('type')
    app_user_id = event.get('app_user_id')
    
    logger.info(f"Received RevenueCat webhook: {event_type} for {app_user_id}")
    
    # Find user subscription
    try:
        subscription = UserSubscription.objects.get(
            revenuecat_app_user_id=app_user_id
        )
    except UserSubscription.DoesNotExist:
        logger.warning(f"Subscription not found for app_user_id: {app_user_id}")
        # Still return 200 to acknowledge receipt
        return Response({'status': 'user_not_found'})
    
    # Process different event types
    event_handlers = {
        'INITIAL_PURCHASE': handle_initial_purchase,
        'RENEWAL': handle_renewal,
        'CANCELLATION': handle_cancellation,
        'UNCANCELLATION': handle_uncancellation,
        'EXPIRATION': handle_expiration,
        'BILLING_ISSUE': handle_billing_issue,
        'PRODUCT_CHANGE': handle_product_change,
        'TRANSFER': handle_transfer,
        'SUBSCRIBER_ALIAS': handle_subscriber_alias,
    }
    
    handler = event_handlers.get(event_type)
    if handler:
        handler(subscription, event, payload)
    else:
        logger.warning(f"Unhandled event type: {event_type}")
    
    # Always return 200 to acknowledge receipt
    return Response({'status': 'received'})


def handle_initial_purchase(subscription, event, payload):
    """Handle initial purchase event."""
    subscription.status = 'active'
    subscription.is_premium = True
    
    if event.get('purchased_at_ms'):
        subscription.original_purchase_date = timezone.datetime.fromtimestamp(
            event['purchased_at_ms'] / 1000, tz=timezone.utc
        )
    
    if event.get('expiration_at_ms'):
        subscription.expires_at = timezone.datetime.fromtimestamp(
            event['expiration_at_ms'] / 1000, tz=timezone.utc
        )
    
    subscription.store = event.get('store')
    subscription.last_synced_at = timezone.now()
    subscription.save()
    
    # Record transaction
    create_transaction(subscription, event, 'INITIAL_PURCHASE', payload)
    
    logger.info(f"Initial purchase recorded for {subscription.user.email}")


def handle_renewal(subscription, event, payload):
    """Handle subscription renewal event."""
    subscription.status = 'active'
    subscription.is_premium = True
    
    if event.get('expiration_at_ms'):
        subscription.expires_at = timezone.datetime.fromtimestamp(
            event['expiration_at_ms'] / 1000, tz=timezone.utc
        )
    
    subscription.last_synced_at = timezone.now()
    subscription.save()
    
    create_transaction(subscription, event, 'RENEWAL', payload)
    
    logger.info(f"Renewal recorded for {subscription.user.email}")


def handle_cancellation(subscription, event, payload):
    """Handle subscription cancellation event."""
    subscription.status = 'cancelled'
    subscription.unsubscribe_detected_at = timezone.now()
    subscription.last_synced_at = timezone.now()
    subscription.save()
    
    create_transaction(subscription, event, 'CANCELLATION', payload)
    
    logger.info(f"Cancellation recorded for {subscription.user.email}")


def handle_uncancellation(subscription, event, payload):
    """Handle subscription uncancellation event."""
    subscription.status = 'active'
    subscription.unsubscribe_detected_at = None
    subscription.last_synced_at = timezone.now()
    subscription.save()
    
    create_transaction(subscription, event, 'UNCANCELLATION', payload)
    
    logger.info(f"Uncancellation recorded for {subscription.user.email}")


def handle_expiration(subscription, event, payload):
    """Handle subscription expiration event."""
    subscription.status = 'expired'
    subscription.is_premium = False
    subscription.last_synced_at = timezone.now()
    subscription.save()
    
    create_transaction(subscription, event, 'EXPIRATION', payload)
    
    logger.info(f"Expiration recorded for {subscription.user.email}")


def handle_billing_issue(subscription, event, payload):
    """Handle billing issue event."""
    subscription.status = 'grace_period'
    subscription.billing_issue_detected_at = timezone.now()
    subscription.last_synced_at = timezone.now()
    subscription.save()
    
    create_transaction(subscription, event, 'BILLING_ISSUE', payload)
    
    logger.info(f"Billing issue recorded for {subscription.user.email}")


def handle_product_change(subscription, event, payload):
    """Handle product change event."""
    new_product_id = event.get('new_product_id')
    
    # Try to find matching plan
    try:
        plan = SubscriptionPlan.objects.get(revenuecat_product_id=new_product_id)
        subscription.plan = plan
    except SubscriptionPlan.DoesNotExist:
        logger.warning(f"Plan not found for product: {new_product_id}")
    
    subscription.last_synced_at = timezone.now()
    subscription.save()
    
    create_transaction(subscription, event, 'PRODUCT_CHANGE', payload)
    
    logger.info(f"Product change recorded for {subscription.user.email}")


def handle_transfer(subscription, event, payload):
    """Handle subscription transfer event."""
    create_transaction(subscription, event, 'TRANSFER', payload)
    logger.info(f"Transfer recorded for {subscription.user.email}")


def handle_subscriber_alias(subscription, event, payload):
    """Handle subscriber alias event."""
    new_app_user_id = event.get('new_app_user_id')
    if new_app_user_id:
        subscription.revenuecat_app_user_id = new_app_user_id
        subscription.save()
    logger.info(f"Subscriber alias updated for {subscription.user.email}")


def create_transaction(subscription, event, event_type, payload):
    """Create a transaction record from webhook event."""
    transaction_id = event.get('id') or f"{event_type}_{timezone.now().timestamp()}"
    
    # Check if transaction already exists
    if SubscriptionTransaction.objects.filter(transaction_id=transaction_id).exists():
        return None
    
    transaction = SubscriptionTransaction.objects.create(
        user_subscription=subscription,
        event_type=event_type,
        transaction_id=transaction_id,
        original_transaction_id=event.get('original_transaction_id'),
        product_id=event.get('product_id', ''),
        price=event.get('price'),
        currency=event.get('currency'),
        store=event.get('store'),
        raw_payload=payload,
    )
    
    if event.get('purchased_at_ms'):
        transaction.purchased_at = timezone.datetime.fromtimestamp(
            event['purchased_at_ms'] / 1000, tz=timezone.utc
        )
    
    if event.get('expiration_at_ms'):
        transaction.expires_at = timezone.datetime.fromtimestamp(
            event['expiration_at_ms'] / 1000, tz=timezone.utc
        )
    
    transaction.save()
    return transaction


@api_view(['GET'])
@permission_classes([AllowAny])
def check_feature_access(request):
    """
    Check if a user has access to a specific premium feature.
    """
    user_id = request.query_params.get('user_id')
    feature = request.query_params.get('feature')
    
    if not user_id or not feature:
        return Response(
            {'error': 'user_id and feature are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    valid_features = [
        'unlimited_appointments', 'premium_therapists',
        'unlimited_chat', 'priority_support', 'exclusive_content'
    ]
    
    if feature not in valid_features:
        return Response(
            {'error': f'Invalid feature. Valid options: {valid_features}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        subscription = UserSubscription.objects.select_related('plan').get(user_id=user_id)
        has_access = subscription.has_feature(feature)
    except UserSubscription.DoesNotExist:
        has_access = False
    
    return Response({
        'user_id': user_id,
        'feature': feature,
        'has_access': has_access,
    })
