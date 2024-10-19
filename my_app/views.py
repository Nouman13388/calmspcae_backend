# my_app/views.py

from django.http import Http404
from rest_framework import viewsets, filters, status, generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Profile, Assessment, HealthData, Feedback, Professional, Appointment, Clinic, Article
from .serializers import (
    UserSerializer, ProfileSerializer, AssessmentSerializer, HealthDataSerializer,
    FeedbackSerializer, ProfessionalSerializer, AppointmentSerializer, ClinicSerializer, ArticleSerializer
)
import requests
from rest_framework.decorators import api_view
from django.views.generic import TemplateView


# Index view for rendering the home page
class IndexView(TemplateView):
    template_name = 'index.html'  # Ensure you have an 'index.html' template in your templates folder


# Fetch content from NHS Mental Health API with authentication
@api_view(['GET'])
# Fetch content from NHS Mental Health API with authentication
@api_view(['GET'])
def get_mental_health_content(request):
    # API endpoint for NHS mental health content
    url = "https://api.nhs.uk/mental-health?api-version=1.0"

    # Use your Primary Key from the NHS API as the subscription key
    headers = {
        'Ocp-Apim-Subscription-Key': 'ba52539dd260499198a6c9ee97bef2b1',  # Replace with your actual Primary Key
        'Content-Type': 'application/json'
    }

    # Send a GET request to the NHS API
    response = requests.get(url, headers=headers)

    # Handle the response
    if response.status_code == 200:
        data = response.json()  # Extract the JSON data from the response
        return Response(data)  # Return the data as the response
    else:
        # Print the response text for debugging
        print(response.text)  # Log the response text to the console
        return Response({'error': 'Failed to retrieve data from NHS API'}, status=response.status_code)

# User view set for user management
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id', 'email']
    search_fields = ['name', 'email']
    ordering_fields = ['id', 'name', 'email']


# Profile management without unnecessary permissions
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['user__name', 'location']


# Read-only viewset for assessments
class AssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['type']


# Health data management
class HealthDataViewSet(viewsets.ModelViewSet):
    queryset = HealthData.objects.all()
    serializer_class = HealthDataSerializer


# Feedback management
class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()


# Professional management
class ProfessionalViewSet(viewsets.ModelViewSet):
    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['user__name', 'specialization']

    def list(self, request, *args, **kwargs):
        professionals = Professional.objects.all()
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        if start_time and end_time:
            appointments = Appointment.objects.filter(
                professional__in=professionals,
                start_time=start_time,
                end_time=end_time
            )
            return Response({
                'professionals': ProfessionalSerializer(professionals, many=True).data,
                'appointments': AppointmentSerializer(appointments, many=True).data
            })
        return super().list(request, *args, **kwargs)


# Appointment management
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'professional', 'status']
    search_fields = ['professional__user__name', 'status']


# Clinic management for location and contact details
class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['latitude', 'longitude', 'email', 'name']
    search_fields = ['name', 'email']


# views.py
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
