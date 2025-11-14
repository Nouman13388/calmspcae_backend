from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from functools import wraps


# ============ Existing Permissions (kept for compatibility) ============

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Only allow the owner of the object to modify it
        return obj.user == request.user


class IsProfessionalOrReadOnly(BasePermission):
    """
    Custom permission to allow only read-only actions (GET) for professionals.
    Non-professionals will have full access.
    """

    def has_permission(self, request, view):
        # Allow read-only access (GET, HEAD, OPTIONS) for professionals
        if request.method in SAFE_METHODS:
            # Check if the user is a professional
            return request.user.is_authenticated and hasattr(request.user, 'professional')
        # Non-professionals have full access (if authenticated)
        return request.user.is_authenticated


# ============ New Role-Based Permissions ============

class IsAdmin(BasePermission):
    """
    Permission to check if user is admin
    """
    message = 'You must be an admin to access this resource.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   (request.user.is_superuser or request.user.user_type == 'admin'))


class IsStaff(BasePermission):
    """
    Permission to check if user is staff
    """
    message = 'You must be staff to access this resource.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   (request.user.is_staff or request.user.user_type == 'staff'))


class IsAdminOrStaff(BasePermission):
    """
    Permission to check if user is admin or staff
    """
    message = 'You must be admin or staff to access this resource.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   (request.user.is_superuser or request.user.is_staff or 
                    request.user.user_type in ['admin', 'staff']))


class IsCustomer(BasePermission):
    """
    Permission to check if user is customer
    """
    message = 'You must be a customer to access this resource.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.user_type == 'customer')


class IsTherapist(BasePermission):
    """
    Permission to check if user is therapist
    """
    message = 'You must be a therapist to access this resource.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.user_type == 'therapist')


class IsEmailVerified(BasePermission):
    """
    Permission to check if user's email is verified
    """
    message = 'Your email is not verified. Please verify your email to access this resource.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   request.user.is_email_verified)


# ============ View Decorators ============

def admin_required(view_func):
    """
    Decorator to require admin access for a view
    Usage: @admin_required
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'Authentication required.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not (request.user.is_superuser or request.user.user_type == 'admin'):
            return Response({
                'success': False,
                'message': 'Admin access required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    """
    Decorator to require staff access for a view
    Usage: @staff_required
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'Authentication required.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not (request.user.is_staff or request.user.user_type == 'staff'):
            return Response({
                'success': False,
                'message': 'Staff access required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def therapist_required(view_func):
    """
    Decorator to require therapist access for a view
    Usage: @therapist_required
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'Authentication required.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user.user_type != 'therapist':
            return Response({
                'success': False,
                'message': 'Therapist access required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def customer_required(view_func):
    """
    Decorator to require customer access for a view
    Usage: @customer_required
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'Authentication required.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user.user_type != 'customer':
            return Response({
                'success': False,
                'message': 'Customer access required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def email_verified_required(view_func):
    """
    Decorator to require email verification
    Usage: @email_verified_required
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'Authentication required.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not request.user.is_email_verified:
            return Response({
                'success': False,
                'message': 'Email verification required.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return view_func(request, *args, **kwargs)
    return wrapper


# ============ Mixin for ViewSets ============

class RoleBasedAccessMixin:
    """
    Mixin to add role-based access control to ViewSets
    
    Usage in ViewSet:
    class MyViewSet(RoleBasedAccessMixin, viewsets.ModelViewSet):
        role_based_permissions = {
            'list': ['admin', 'staff'],
            'create': ['admin'],
            'destroy': ['admin'],
        }
    """
    role_based_permissions = {}
    
    def check_permissions(self, request):
        super().check_permissions(request)
        
        action = self.action
        allowed_roles = self.role_based_permissions.get(action)
        
        if allowed_roles is None:
            return  # No role-based restriction for this action
        
        if not request.user.is_authenticated:
            self.permission_denied(request, message='Authentication required.')
        
        user_role = request.user.user_type
        if request.user.is_superuser:
            user_role = 'admin'
        
        if user_role not in allowed_roles and not request.user.is_superuser:
            self.permission_denied(request, message=f'This action requires one of these roles: {", ".join(allowed_roles)}')
