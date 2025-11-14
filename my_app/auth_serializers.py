"""
Authentication and User Serializers
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile, Assessment, HealthData, Feedback, Professional, Appointment, Clinic, Article, \
    ChatMessage, Therapist, UserAppointment, EmailVerificationToken, PasswordResetToken


# ============ Basic Serializers ============
class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for read operations"""
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone_number', 'profile_picture', 'user_type', 'is_email_verified', 'created_at']
        read_only_fields = ['id', 'is_email_verified', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with all fields"""
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone_number', 'profile_picture', 'user_type', 
                  'is_email_verified', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_email_verified', 'created_at', 'updated_at']


# ============ Authentication Serializers ============
class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'name', 'phone_number', 'user_type', 'password', 'password_confirm']
    
    def validate(self, data):
        """Validate that passwords match"""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        
        # Remove the confirmation password before saving
        data.pop('password_confirm')
        return data
    
    def create(self, validated_data):
        """Create new user"""
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validate credentials"""
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError('Email and password are required.')
        
        user = User.objects.filter(email=email).first()
        
        if not user or not user.check_password(password):
            raise serializers.ValidationError('Invalid email or password.')
        
        if not user.is_email_verified:
            raise serializers.ValidationError('Please verify your email before logging in.')
        
        data['user'] = user
        return data


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for email verification"""
    token = serializers.CharField(required=True)
    uid = serializers.IntegerField(required=True)


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Check if user with this email exists"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('No user found with this email address.')
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset"""
    token = serializers.CharField(required=True)
    uid = serializers.IntegerField(required=True)
    new_password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        """Validate that new passwords match"""
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password (authenticated users)"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        """Validate passwords"""
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'New passwords do not match.'})
        
        user = self.context.get('request').user
        if not user.check_password(data.get('old_password')):
            raise serializers.ValidationError({'old_password': 'Old password is incorrect.'})
        
        return data


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    class Meta:
        model = User
        fields = ['name', 'phone_number', 'profile_picture', 'email']
        read_only_fields = ['email']  # Email cannot be changed here


# ============ Other Serializers ============
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


class TherapistSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Therapist
        fields = ['id', 'email', 'name', 'specialization', 'bio', 'created_at', 'updated_at', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        therapist = Therapist(**validated_data)
        if password:
            therapist.set_password(password)
        therapist.save()
        return therapist


class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'


class UserAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAppointment
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
        fields = '__all__'
