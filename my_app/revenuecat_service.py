"""
RevenueCat Service - Handles communication with RevenueCat API
"""

import requests
import logging
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RevenueCatService:
    """
    Service class for interacting with RevenueCat API.
    
    Documentation: https://www.revenuecat.com/docs/api-v1
    """
    
    BASE_URL = "https://api.revenuecat.com/v1"
    
    def __init__(self):
        self.api_key = getattr(settings, 'REVENUECAT_API_KEY', None)
        self.webhook_secret = getattr(settings, 'REVENUECAT_WEBHOOK_SECRET', None)
        
        if not self.api_key:
            logger.warning("REVENUECAT_API_KEY not configured in settings")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers for RevenueCat API."""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-Platform': 'stripe'  # Default platform, can be overridden
        }
    
    def get_subscriber(self, app_user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscriber information from RevenueCat.
        
        Args:
            app_user_id: The app user ID (usually the user's UUID or email)
            
        Returns:
            Subscriber data dict or None if not found
        """
        if not self.api_key:
            logger.error("RevenueCat API key not configured")
            return None
            
        try:
            url = f"{self.BASE_URL}/subscribers/{app_user_id}"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return response.json().get('subscriber', {})
            elif response.status_code == 404:
                logger.info(f"Subscriber not found: {app_user_id}")
                return None
            else:
                logger.error(f"Error fetching subscriber: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request error fetching subscriber: {str(e)}")
            return None
    
    def create_subscriber(self, app_user_id: str, attributes: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Create or get a subscriber in RevenueCat.
        
        Args:
            app_user_id: The app user ID
            attributes: Optional subscriber attributes
            
        Returns:
            Subscriber data or None
        """
        if not self.api_key:
            logger.error("RevenueCat API key not configured")
            return None
            
        try:
            url = f"{self.BASE_URL}/subscribers/{app_user_id}"
            
            # GET request creates subscriber if doesn't exist
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code in [200, 201]:
                subscriber_data = response.json().get('subscriber', {})
                
                # Update attributes if provided
                if attributes:
                    self.update_subscriber_attributes(app_user_id, attributes)
                
                return subscriber_data
            else:
                logger.error(f"Error creating subscriber: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request error creating subscriber: {str(e)}")
            return None
    
    def update_subscriber_attributes(self, app_user_id: str, attributes: Dict) -> bool:
        """
        Update subscriber attributes in RevenueCat.
        
        Args:
            app_user_id: The app user ID
            attributes: Dict of attributes to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            return False
            
        try:
            url = f"{self.BASE_URL}/subscribers/{app_user_id}/attributes"
            
            # Format attributes for RevenueCat
            formatted_attributes = {
                key: {'value': str(value)} for key, value in attributes.items()
            }
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                json={'attributes': formatted_attributes},
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.RequestException as e:
            logger.error(f"Error updating subscriber attributes: {str(e)}")
            return False
    
    def get_offerings(self, app_user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get available offerings for a subscriber.
        
        Args:
            app_user_id: The app user ID
            
        Returns:
            Offerings data or None
        """
        if not self.api_key:
            return None
            
        try:
            url = f"{self.BASE_URL}/subscribers/{app_user_id}/offerings"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching offerings: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request error fetching offerings: {str(e)}")
            return None
    
    def grant_promotional_entitlement(
        self, 
        app_user_id: str, 
        entitlement_id: str, 
        duration: str = "monthly",
        start_time_ms: Optional[int] = None
    ) -> bool:
        """
        Grant a promotional entitlement to a user.
        
        Args:
            app_user_id: The app user ID
            entitlement_id: The entitlement identifier
            duration: "daily", "weekly", "monthly", "two_month", "three_month", 
                      "six_month", "yearly", "lifetime"
            start_time_ms: Start time in milliseconds (defaults to now)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            return False
            
        try:
            url = f"{self.BASE_URL}/subscribers/{app_user_id}/entitlements/{entitlement_id}/promotional"
            
            payload = {'duration': duration}
            if start_time_ms:
                payload['start_time_ms'] = start_time_ms
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info(f"Granted promotional entitlement {entitlement_id} to {app_user_id}")
                return True
            else:
                logger.error(f"Error granting entitlement: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Request error granting entitlement: {str(e)}")
            return False
    
    def revoke_promotional_entitlement(self, app_user_id: str, entitlement_id: str) -> bool:
        """
        Revoke a promotional entitlement from a user.
        
        Args:
            app_user_id: The app user ID
            entitlement_id: The entitlement identifier
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            return False
            
        try:
            url = f"{self.BASE_URL}/subscribers/{app_user_id}/entitlements/{entitlement_id}/revoke_promotionals"
            
            response = requests.post(url, headers=self._get_headers(), timeout=10)
            
            return response.status_code == 200
            
        except requests.RequestException as e:
            logger.error(f"Request error revoking entitlement: {str(e)}")
            return False
    
    def delete_subscriber(self, app_user_id: str) -> bool:
        """
        Delete a subscriber from RevenueCat.
        
        Args:
            app_user_id: The app user ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            return False
            
        try:
            url = f"{self.BASE_URL}/subscribers/{app_user_id}"
            response = requests.delete(url, headers=self._get_headers(), timeout=10)
            
            return response.status_code == 200
            
        except requests.RequestException as e:
            logger.error(f"Request error deleting subscriber: {str(e)}")
            return False
    
    def parse_subscriber_data(self, subscriber_data: Dict) -> Dict[str, Any]:
        """
        Parse subscriber data from RevenueCat into a structured format.
        
        Args:
            subscriber_data: Raw subscriber data from RevenueCat
            
        Returns:
            Parsed subscription info
        """
        result = {
            'is_premium': False,
            'status': 'expired',
            'active_entitlements': [],
            'active_subscriptions': [],
            'expires_at': None,
            'original_purchase_date': None,
            'management_url': subscriber_data.get('management_url'),
        }
        
        # Check entitlements
        entitlements = subscriber_data.get('entitlements', {})
        for entitlement_id, entitlement_data in entitlements.items():
            if entitlement_data.get('expires_date'):
                expires = datetime.fromisoformat(
                    entitlement_data['expires_date'].replace('Z', '+00:00')
                )
                if expires > timezone.now():
                    result['active_entitlements'].append({
                        'id': entitlement_id,
                        'expires_at': expires,
                        'product_identifier': entitlement_data.get('product_identifier'),
                    })
                    result['is_premium'] = True
                    
                    # Track the latest expiration
                    if not result['expires_at'] or expires > result['expires_at']:
                        result['expires_at'] = expires
            elif entitlement_data.get('product_identifier'):
                # Lifetime entitlement (no expiry)
                result['active_entitlements'].append({
                    'id': entitlement_id,
                    'expires_at': None,
                    'product_identifier': entitlement_data.get('product_identifier'),
                })
                result['is_premium'] = True
        
        # Check subscriptions
        subscriptions = subscriber_data.get('subscriptions', {})
        for product_id, sub_data in subscriptions.items():
            if sub_data.get('expires_date'):
                expires = datetime.fromisoformat(
                    sub_data['expires_date'].replace('Z', '+00:00')
                )
                if expires > timezone.now():
                    result['active_subscriptions'].append({
                        'product_id': product_id,
                        'expires_at': expires,
                        'store': sub_data.get('store'),
                        'is_sandbox': sub_data.get('is_sandbox', False),
                    })
        
        # Determine status
        if result['is_premium']:
            result['status'] = 'active'
        elif subscriber_data.get('entitlements'):
            result['status'] = 'expired'
        else:
            result['status'] = 'never_subscribed'
        
        # Original purchase date
        if subscriber_data.get('original_purchase_date'):
            result['original_purchase_date'] = datetime.fromisoformat(
                subscriber_data['original_purchase_date'].replace('Z', '+00:00')
            )
        
        return result
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify RevenueCat webhook signature.
        
        Args:
            payload: Raw request body
            signature: Signature from X-RevenueCat-Signature header
            
        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured, skipping verification")
            return True  # Allow in development
            
        import hmac
        import hashlib
        
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)


# Singleton instance
revenuecat_service = RevenueCatService()
