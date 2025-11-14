from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProfileViewSet, AssessmentViewSet,
    HealthDataViewSet, FeedbackViewSet,
 ClinicViewSet, ArticleViewSet, ChatViewSet, TherapistViewSet, UserAppointmentViewSet
)
from .auth_views import (
    register_view, login_view, verify_email_view, resend_verification_email_view,
    forgot_password_view, reset_password_view, get_profile_view, update_profile_view,
    change_password_view, logout_view
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'assessments', AssessmentViewSet)
router.register(r'healthdata', HealthDataViewSet)
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'clinics', ClinicViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'therapists', TherapistViewSet)
router.register(r'appointments', UserAppointmentViewSet)
router.register(r'chat', ChatViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/verify-email/', verify_email_view, name='verify-email'),
    path('auth/resend-verification-email/', resend_verification_email_view, name='resend-verification-email'),
    path('auth/forgot-password/', forgot_password_view, name='forgot-password'),
    path('auth/reset-password/', reset_password_view, name='reset-password'),
    path('auth/profile/', get_profile_view, name='get-profile'),
    path('auth/update-profile/', update_profile_view, name='update-profile'),
    path('auth/change-password/', change_password_view, name='change-password'),
]
