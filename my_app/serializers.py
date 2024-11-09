from rest_framework import serializers
from .models import User, Profile, Assessment, HealthData, Feedback, Professional, Appointment, Clinic, Article, \
    ChatMessage, Therapist, UserAppointment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = '__all__'

class HealthDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthData
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


from rest_framework import serializers
from .models import Therapist


class TherapistSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Ensure password is write-only

    class Meta:
        model = Therapist
        fields = ['id', 'email', 'name', 'specialization', 'bio', 'created_at', 'updated_at', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # Pop the password from validated_data
        password = validated_data.pop('password', None)
        therapist = Therapist(**validated_data)

        # If password is provided, set it using set_password
        if password:
            therapist.set_password(password)

        therapist.save()
        return therapist

    def update(self, instance, validated_data):
        # Handle password separately to ensure hashing
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update password if provided
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = '__all__'

class UserAppointmentSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format="%d/%m/%Y %H:%M")
    end_time = serializers.DateTimeField(format="%d/%m/%Y %H:%M")

    class Meta:
        model = UserAppointment
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'therapist', 'message', 'created_at']
