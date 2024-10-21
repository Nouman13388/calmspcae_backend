from rest_framework import serializers
from .models import User, Profile, Assessment, HealthData, Feedback, Professional, Appointment, Clinic, Article


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


class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': True}  # Ensure user is required
        }

    def validate_user(self, value):
        # Check if a professional with this user already exists (for create only)
        if self.instance is None and Professional.objects.filter(user=value).exists():
            raise serializers.ValidationError("A professional with this user already exists.")
        return value

    def create(self, validated_data):
        # Ensure the user is included in validated_data
        user = validated_data.get('user')
        if not user:
            raise serializers.ValidationError({'user': 'This field is required.'})

        # Create professional instance
        professional = Professional.objects.create(**validated_data)
        return professional

    def update(self, instance, validated_data):
        # Update existing professional
        instance.specialization = validated_data.get('specialization', instance.specialization)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()
        return instance

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time.")
        return data


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
