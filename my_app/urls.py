# my_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ArticleViewSet

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.ProfileViewSet)
router.register(r'assessments', views.AssessmentViewSet)
router.register(r'healthdata', views.HealthDataViewSet)
router.register(r'feedback', views.FeedbackViewSet, basename='feedback')
router.register(r'professionals', views.ProfessionalViewSet)
router.register(r'appointments', views.AppointmentViewSet)
router.register(r'clinics', views.ClinicViewSet)
router.register(r'articles', ArticleViewSet)


urlpatterns = [
    path('', include(router.urls)),  # Include the router for all model endpoints
    path('api/content/', views.get_mental_health_content),  # NHS API fetching endpoint
]
