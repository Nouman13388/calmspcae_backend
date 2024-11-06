from django.http import Http404
from rest_framework import viewsets, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Profile, Assessment, HealthData, Feedback, Professional, Appointment, Clinic, Article, \
    ChatMessage, Therapist, UserAppointment
from .serializers import (
    UserSerializer, ProfileSerializer, AssessmentSerializer, HealthDataSerializer,
    FeedbackSerializer, ProfessionalSerializer, AppointmentSerializer, ClinicSerializer, ArticleSerializer,
    ChatMessageSerializer, TherapistSerializer, UserAppointmentSerializer
)
import requests
from rest_framework.decorators import api_view
from django.views.generic import TemplateView
from rest_framework.permissions import AllowAny  # Import AllowAny


# Index view for rendering the home page
class IndexView(TemplateView):
    template_name = 'index.html'


# Fetch content from NHS Mental Health API with authentication
@api_view(['GET'])
def get_mental_health_content(request):
    url = "https://api.nhs.uk/mental-health?api-version=1.0"
    headers = {
        'Ocp-Apim-Subscription-Key': 'ba52539dd260499198a6c9ee97bef2b1',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return Response(data)
    else:
        print(response.text)
        return Response({'error': 'Failed to retrieve data from NHS API'}, status=response.status_code)


# User view set for user management
from rest_framework.decorators import action

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id', 'email']
    search_fields = ['name', 'email']
    ordering_fields = ['id', 'name', 'email']

    @action(detail=False, methods=['get'])
    def get_by_email(self, request):
        email = request.query_params.get('email', None)
        if email:
            try:
                user = User.objects.get(email=email)
                serializer = self.get_serializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=404)
        return Response({"error": "Email parameter is required"}, status=400)


# Profile management without unnecessary permissions
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]  # Allow access without authentication
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['user__name', 'location']


# Read-only viewset for assessments
class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [AllowAny]  # Allow access without authentication
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['type']


# Health data management
class HealthDataViewSet(viewsets.ModelViewSet):
    queryset = HealthData.objects.all()
    serializer_class = HealthDataSerializer
    permission_classes = [AllowAny]  # Allow access without authentication


# Feedback management
class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    permission_classes = [AllowAny]  # Allow access without authentication


class ProfessionalViewSet(viewsets.ModelViewSet):
    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
    permission_classes = [AllowAny]  # Allow access without authentication

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        if not user_id:
            return Response({'error': 'User ID must be provided.'}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        # Add the user to the validated data and attempt to save
        data = request.data.copy()
        data['user'] = user_id
        serializer = self.get_serializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)  # Return validation errors

        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class UserAppointmentViewSet(viewsets.ModelViewSet):
    queryset = UserAppointment.objects.all()
    serializer_class = UserAppointmentSerializer
    permission_classes = [AllowAny]  # Allow access without authentication (adjust as needed)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'therapist', 'status']  # Filter by user, therapist, and status
    search_fields = ['user__name', 'therapist__name', 'status']

# Appointment management
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [AllowAny]  # Allow access without authentication
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'professional', 'status']
    search_fields = ['professional__user__name', 'status']


# Clinic management for location and contact details
class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [AllowAny]  # Allow access without authentication
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['latitude', 'longitude', 'email', 'name']
    search_fields = ['name', 'email']


# Article management
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [AllowAny]  # Allow access without authentication


class TherapistViewSet(viewsets.ModelViewSet):
    queryset = Therapist.objects.all()
    serializer_class = TherapistSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['id', 'email']
    search_fields = ['name', 'email']

    def create(self, request, *args, **kwargs):
        # Directly pass the data to the serializer without checking for user_id
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# Chat view set for managing chat messages
class ChatViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [AllowAny]  # Adjust permissions as needed

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def list(self, request, *args, **kwargs):
        user = request.query_params.get('user_id')
        therapist = request.query_params.get('therapist_id')

        if user and therapist:
            messages = self.queryset.filter(user_id=user, therapist_id=therapist)
            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data)

        return Response({"error": "User ID and Therapist ID are required"}, status=400)
