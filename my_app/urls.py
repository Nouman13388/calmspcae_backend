from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProfileViewSet, AssessmentViewSet,
    HealthDataViewSet, FeedbackViewSet,
 ClinicViewSet, ArticleViewSet, ChatViewSet, TherapistViewSet, UserAppointmentViewSet
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
router.register(r'chat', ChatViewSet, basename='chat')  # Add this line

urlpatterns = [
    path('', include(router.urls)),
    # Add any other paths you need
]
