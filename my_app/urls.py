# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProfileViewSet, AssessmentViewSet,
    HealthDataViewSet, FeedbackViewSet, ProfessionalViewSet,
    AppointmentViewSet, ClinicViewSet, ArticleViewSet, get_mental_health_content
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'assessments', AssessmentViewSet)
router.register(r'healthdata', HealthDataViewSet)
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'professionals', ProfessionalViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'clinics', ClinicViewSet)
router.register(r'articles', ArticleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/content/', get_mental_health_content),  # NHS API fetching endpoint
]
